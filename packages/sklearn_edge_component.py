from liota.core.package_manager import LiotaPackage

dependencies = ["edge_systems/dell5k/edge_system"] #will graphite also be dependencies??


class PackageClass(LiotaPackage):

    def run(self, registry):
        from liota.edge_component.sklearn_edge_component import SKLearnEdgeComponent
        # initialize and run the physical model (simulated device)
        sklearn_edge_component = SKLearnEdgeComponent(config['modelPath'], None)
        
        registry.register("sklearn_edge_component", sklearn_edge_component)

    def clean_up(self):
        pass