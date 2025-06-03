from input_resolver import InputResolver
from converter import Converter
from inference import Inference
from postprocessor import PostProcessor
from noise_generator import NoiseGenerator

class AudioPipeline:
    def __init__(self, config):
        self.config = config
        self.input_resolver = InputResolver(config["input_audio"])
        self.converter = Converter(config["conversion"])
        self.inference = Inference(config["inference"])
        self.postprocessor = PostProcessor(config["postprocessing"])
        self.noise_generator = NoiseGenerator(config["noise_output"])

    def run(self):
        # 1. Resolve input files
        input_files = self.input_resolver.resolve()

        # 2. Convert audio files
        converted_files = self.converter.convert_all(input_files) if self.converter.enabled else input_files

        # 3. Inference using ClearVoice
        inferred_files = self.inference.run(converted_files) if self.inference.enabled else converted_files

        # 4. Postprocess the inferred files
        postprocessed_files = self.postprocessor.process_all(inferred_files) if self.postprocessor.enabled else inferred_files

        # 5. Generate noise output (subtract denoised from original)
        noise_files = []
        if self.noise_generator.enabled:
            noise_files = self.noise_generator.generate_noise(converted_files, inferred_files)

        return {
            "input_files": input_files,
            "converted_files": converted_files,
            "inferred_files": inferred_files,
            "postprocessed_files": postprocessed_files,
            "noise_files": noise_files
        }
