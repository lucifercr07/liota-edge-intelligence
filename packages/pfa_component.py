from liota.core.package_manager import LiotaPackage

dependencies = ["edge_systems/dell5k/edge_system"] #will graphite also be dependencies??


class PackageClass(LiotaPackage):

    def run(self, registry):
        from liota.edge_component.pfa_component import PFAComponent
        # initialize and run the physical model (simulated device)
        pfa_component = PFAComponent(config['modelPath'], None)
        
        registry.register("pfa_component", pfa_component)

    def clean_up(self):
        pass