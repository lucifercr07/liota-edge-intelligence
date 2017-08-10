from liota.core.package_manager import LiotaPackage

dependencies = ["edge_systems/dell5k/edge_system"] 


class PackageClass(LiotaPackage):

    def run(self, registry):
        from liota.edge_component.tf_edge_component import TensorFlowEdgeComponent
        # initialize and run the physical model (simulated device)
        tensorflow_edge_component = TensorFlowEdgeComponent(config['modelPath'], None)
        
        registry.register("tensorflow_edge_component", tensorflow_edge_component)

    def clean_up(self):
        pass