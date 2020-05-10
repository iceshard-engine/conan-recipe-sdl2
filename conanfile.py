from conans import ConanFile, MSBuild, CMake, tools
import shutil
import os

class SDL2Conan(ConanFile):
    name = "SDL2"
    license = "MIT"
    url = "https://www.libsdl.org/index.php"
    description = "Conan recipe for the SDL2 library."

    # Settings and options
    settings = "os", "compiler", "arch"

    options = {
        "shared": [True, False],
        "sdl2main": [True, False]
    }
    default_options = {
        "shared": True,
        "sdl2main": False
    }

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.3@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    # Initialize the package
    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires

    # Update the package id
    def package_id(self):
        self.info.options.sdl2main = "Any"

    # Build both the debug and release builds
    def ice_build(self):
        if self.settings.compiler == "Visual Studio":
            self.ice_build_msbuild("VisualC/SDL.sln", ["Debug", "Release"])

        else:
            self.ice_build_cmake(["Debug", "Release"])

    def package(self):
        # Copy the license file
        self.copy("COPYING.txt", src=self._ice.source_dir, dst="LICENSE")

        self.copy("*.h", "include", "{}/include".format(self._ice.source_dir), keep_path=False)

        # Calculate the build directory
        build_dir = self._ice.source_dir

        # Build dir on msvc
        if self.settings.compiler == "Visual Studio":
            build_dir = os.path.join(build_dir, "VisualC/x64")

        # Build dir on clang
        if self.settings.compiler == "clang":
            pass

        # Copy files
        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy("*/SDL2.dll", "bin", build_dir, keep_path=True)
                self.copy("*/SDL2.pdb", "bin", build_dir, keep_path=True)
            else:
                self.copy("*/SDL2.pdb", "lib", build_dir, keep_path=True)
            self.copy("*/SDL2.lib", "lib", build_dir, keep_path=True)
            self.copy("*/SDL2main.lib", "lib", build_dir, keep_path=True)

        if self.settings.os == "Linux":
            if self.options.shared:
                self.copy("*/libSDL2.so", "bin", build_dir, keep_path=True)
            self.copy("*/libSDL2.a", "lib", build_dir, keep_path=True)
            self.copy("*/libSDL2main.a", "lib", build_dir, keep_path=True)

    def package_info(self):
        self.cpp_info.includedirs = ["include"]

        self.cpp_info.debug.libdirs = [ "lib/Debug" ]
        self.cpp_info.release.libdirs = [ "lib/Release" ]
        self.cpp_info.libdirs = []

        if self.options.shared:
            self.cpp_info.debug.bindirs = [ "bin/Debug" ]
            self.cpp_info.release.bindirs = [ "bin/Release" ]
            self.cpp_info.bindirs = []

        if self.options.sdl2main == True:
            self.cpp_info.libs = ["SDL2", "SDL2main"]
        else:
            self.cpp_info.libs = ["SDL2"]
