
from liota.core.package_manager import LiotaPackage

dependencies = ["edge_systems/dell5k/edge_system"] #will graphite also be dependencies??


class PackageClass(LiotaPackage):

    def run(self, registry):
        from liota.edge_component.rule_edge_component import RuleEdgeComponent
          

        # initialize and run the physical model (simulated device)
        rule_edge_component = RuleEdgeComponent(lambda x : 1 if (x>=45) else 0, 1, None)
        
        registry.register("rule_edge_component", rule_edge_component)

    def clean_up(self):
        pass
