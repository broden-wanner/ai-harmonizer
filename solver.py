import search
from sortedcontainers import SortedSet
from search import depth_first_tree_search
from utils import extend, first
from csp import Constraint, NaryCSP, SimpleHarmonizerCSP
from display import show_sovler_solution
from music21.key import Key


def sat_up(to_do: set):
    """An arc heuristic used to order by the scope of a constraint in increasing order

    Args:
        to_do: A set of to-do's, which are (variable, constraint) pairs

    Returns:
        A new SortedSet with the ordered to-do's
    """
    def reciprocal_scope_length(t):
        scope_length = len([var for var in t[1].scope])
        return 1 / scope_length

    return SortedSet(to_do, key=reciprocal_scope_length)


def partition_domain(dom: list):
    """Partitions domain dom into two
    
    Args:
        dom: A list of values that is a domain for a variables

    Returns:
        A tuple of the split domain (first half, second half)
    """
    split = len(dom) // 2
    dom1 = set(list(dom)[:split])
    dom2 = dom - dom1
    return dom1, dom2


class ACSolver:
    """
    Solves a CSP with arc consistency and domain splitting
    
    Attributes:
        csp: The CSP problem to be solved
    """
    def __init__(self, csp: NaryCSP):
        """A CSP solver that uses arc consistency"""
        self.csp = csp

    def GAC(self,
            orig_domains=None,
            to_do=None,
            arc_heuristic=sat_up,
            debug=False):
        """
        Makes this CSP arc-consistent using Generalized Arc Consistency

        Args:
            orig_domains: The original domains
            to_do: A set of (variable, constraint) pairs
            arc_heuristic: A function that takes a set of to_do's and orders them
        
        Returns:
            The reduced domains (an arc-consistent {variable : domain} dictionary)
        """

        if orig_domains is None:
            orig_domains = self.csp.domains
        if to_do is None:
            # Make the set of to_do's
            to_do = {(var, const)
                     for const in self.csp.constraints for var in const.scope}
        else:
            to_do = to_do.copy()

        domains = orig_domains.copy()
        to_do = arc_heuristic(to_do)
        checks = 0

        while to_do:
            debug and print(f'To-do set size: {len(to_do)}')

            var, const = to_do.pop()
            debug and print(f'Variable to examine: {var}')

            other_vars = [ov for ov in const.scope if ov != var]
            new_domain = set()
            if len(other_vars) == 0:
                for val in domains[var]:
                    if const.holds({var: val}):
                        new_domain.add(val)
                    checks += 1
                # new_domain = {val for val in domains[var]
                #               if const.holds({var: val})}
            elif len(other_vars) == 1:
                other = other_vars[0]
                for val in domains[var]:
                    for other_val in domains[other]:
                        checks += 1
                        if const.holds({var: val, other: other_val}):
                            new_domain.add(val)
                            break
                # new_domain = {val for val in domains[var]
                #               if any(const.holds({var: val, other: other_val})
                #                      for other_val in domains[other])}
            else:
                # General case
                for val in domains[var]:
                    if debug:
                        print(f'Seeing if {var} = {val} holds:')
                        print(f'\tdomain for {var} is {domains[var]}')
                    holds, checks = self.any_holds(domains,
                                                   const, {var: val},
                                                   other_vars,
                                                   checks=checks,
                                                   debug=debug)

                    debug and print(f'\n{var} = {val} holds?: {holds}')
                    if holds:
                        new_domain.add(val)
                # new_domain = {val for val in domains[var]
                #               if self.any_holds(domains, const, {var: val}, other_vars)}

            if new_domain != domains[var]:
                domains[var] = new_domain
                if not new_domain:
                    return False, domains, checks
                add_to_do = self.new_to_do(var, const).difference(to_do)
                to_do |= add_to_do

            debug and print()
        return True, domains, checks

    def new_to_do(self, var: str, const: Constraint):
        """
        Args:
            var: A variable
            const: A constraint

        Returns:
            New elements to be added to to_do after assigning
            variable var in constraint const.
        """
        return {(nvar, nconst)
                for nconst in self.csp.variables_to_constraints[var]
                if nconst != const for nvar in nconst.scope if nvar != var}

    def any_holds(self,
                  domains,
                  const,
                  env,
                  other_vars,
                  ind=0,
                  checks=0,
                  debug=False):
        """Checks to see if an assigment holds for the constraint

        Args:
            domains: A list of domains
            const: A constraint to check
            env: A {var: val} dictionary
            other_vars: List of all other variables
            ind: Index to start at for other_vars
            checks: Number of checks done so far

        Returns:
            True if Constraint const holds for an assignment
            that extends env with the variables in other_vars[ind:]
            env is a dictionary.
            Warning: this has side effects and changes the elements of env
        """
        if debug and checks % 1000 == 0:
            print(f'\rChecks: {checks}', end='')

        if ind == len(other_vars):
            return const.holds(env), checks + 1
        else:
            var = other_vars[ind]
            for val in domains[var]:
                # env = dict_union(env, {var:val})  # no side effects
                env[var] = val
                holds, checks = self.any_holds(domains,
                                               const,
                                               env,
                                               other_vars,
                                               ind + 1,
                                               checks,
                                               debug=debug)
                if holds:
                    return True, checks
            return False, checks

    def domain_splitting(self, domains=None, to_do=None, arc_heuristic=sat_up):
        """Finds a solution to the current CSP

        Args:
            domains: A list of domains
            to_do: The set of to-do's
            arc_heuristic: A function that is the arc heuristic

        Returns:
            A solution to the current CSP or False if there are no solutions
            to_do is the list of arcs to check.
        """
        if domains is None:
            domains = self.csp.domains
        consistency, new_domains, _ = self.GAC(domains, to_do, arc_heuristic)
        if not consistency:
            return False
        elif all(len(new_domains[var]) == 1 for var in domains):
            return {var: first(new_domains[var]) for var in domains}
        else:
            var = first(x for x in self.csp.variables
                        if len(new_domains[x]) > 1)
            if var:
                dom1, dom2 = partition_domain(new_domains[var])
                new_doms1 = extend(new_domains, var, dom1)
                new_doms2 = extend(new_domains, var, dom2)
                to_do = self.new_to_do(var, None)
                return self.domain_splitting(new_doms1, to_do, arc_heuristic) or \
                       self.domain_splitting(new_doms2, to_do, arc_heuristic)


class ACSearchSolver(search.Problem):
    """A search problem with generalized arcy consistency and domain splitting

    Attributes:
        csp: An instance of an NaryCSP
        cons: An instance of ACSolver seeded with the csp
        heuristic: A function meant to be used as the heuristic
        domains: The dictionary mapping variables to their domains
    """
    def __init__(self, csp: NaryCSP, arc_heuristic=sat_up, debug=False):
        self.csp = csp
        self.acsolver = ACSolver(csp)
        consistent, domains, checks = self.acsolver.GAC(
            arc_heuristic=arc_heuristic, debug=debug)
        if not consistent:
            raise Exception('CSP is inconsistent')

        self.domains = domains
        self.heuristic = arc_heuristic
        super().__init__(self.domains)

    def goal_test(self, node) -> bool:
        """Node is a goal if all domains have 1 element"""
        return all(len(node[var]) == 1 for var in node)

    def actions(self, state):
        """Enumerate all actions for a certain state"""
        var = first(x for x in state if len(state[x]) > 1)
        neighs = []
        if var:
            domain1, domain2 = partition_domain(state[var])
            to_do = self.acsolver.new_to_do(var, None)
            for d in [domain1, domain2]:
                new_domains = extend(state, var, d)
                consistent, cons_domains, checks = self.acsolver.GAC(
                    new_domains, to_do, self.heuristic)
                if consistent:
                    neighs.append(cons_domains)
        return neighs

    def result(self, state, action):
        """Return the result of taking an action in a state"""
        return action

    def search_solve(self):
        """Find solution using depth-first search"""
        solution = None
        try:
            solution = depth_first_tree_search(self).state
        except Exception as e:
            print(f'Exception raised in ACSearchSolver: {e}')
            return solution
        if solution:
            return {var: first(solution[var]) for var in solution}


if __name__ == '__main__':
    shcsp = SimpleHarmonizerCSP(
        name='Test',
        notes=8,
        numerals=['I', 'IV', 'vii', 'iii', 'vi', 'ii', 'V', 'I'],
        part_list=['s', 't', 'b'],
        key=Key('Db'))
    shcsp.display()

    s = ACSolver(shcsp)
    print('[INFO] Beginning GAC')
    consistent, newdomains, checks = s.GAC()
    print(f'Is consistent?: {consistent}')
    print(f'Checks: {checks}')
    print('New Domain Sizes:')
    for v in shcsp.variables:
        print(f'{v}: {len(newdomains[v])}')
    print('[INFO] Finished GAC')

    if consistent:
        print('[INFO] The CSP is consistent!')
        sol1 = s.domain_splitting()
        print('[INFO] Found domain splitting solution')

        # s_prime = ACSearchSolver(shcsp)
        # sol2 = s_prime.search_solve()
        # print('[INFO] Found search solution')

        print('Domain splitting solution:')
        print(sol1)
        show_sovler_solution(solution=sol1, csp=shcsp, bpm=50, method='music')
        # print('\nDepth-First Search solution:')
        # show_sovler_solution(solution=sol2, csp=shcsp, method='music')

    else:
        print('CSP is not consistent')
