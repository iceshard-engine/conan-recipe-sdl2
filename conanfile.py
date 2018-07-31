from conans import ConanFile, MSBuild, CMake, tools
import shutil
import os

class Sdl2Conan(ConanFile):
    name = "sdl2"
    version = "2.0.8"
    license = "MIT"
    description = "SDL2 conan package"
    url = "https://www.libsdl.org/index.php"

    settings = "os", "compiler", "arch"
    options = {"shared": [True, False], "sdl2main": [True,False]}
    default_options = "shared=True", "sdl2main=False"

    SDL2_FOLDER_NAME = "SDL2-%s" % version

    def build_requirements(self):
        if self.settings.os == "Linux":
            self.build_requires("cmake_installer/3.10.0@conan/stable")

    def package_id(self):
        self.info.options.sdl2main = "Any"

    # We dont want the runtime setting for VS projects.
    def configure(self):
        if self.settings.compiler == "Visual Studio":
            del self.settings.compiler.runtime

    # The the source from github
    def source(self):
        zip_name = "SDL2-%s.tar.gz" % self.version
        tools.download("https://www.libsdl.org/release/%s" % zip_name, zip_name)
        tools.unzip(zip_name)
        os.unlink(zip_name)

    # Build both the debug and release builds
    def build(self):
        with tools.chdir(os.path.join(self.source_folder, self.SDL2_FOLDER_NAME)):

            if self.settings.compiler == "Visual Studio":
                msbuild = MSBuild(self)
                msbuild.build("VisualC/SDL.sln", build_type="Debug")
                msbuild.build("VisualC/SDL.sln", build_type="Release")

            else:

                os.mkdir("build")
                with tools.chdir("build"):

                    cmake = CMake(self)
                    if cmake.is_multi_configuration:
                        cmmd = 'cmake "%s" %s' % ("..", cmake.command_line)
                        self.run(cmmd)
                        self.run("cmake --build . --config Debug")
                        self.run("cmake --build . --config Release")

                    else:
                        for config in ("Debug", "Release"):
                            self.output.info("Building %s" % config)
                            self.run('cmake "%s" %s -DCMAKE_BUILD_TYPE=%s'
                                    % ("..", cmake.command_line, config))
                            self.run("cmake --build .")
                            shutil.rmtree("CMakeFiles")
                            os.remove("CMakeCache.txt")


    def package(self):
        # Copy the license file
        self.copy("COPYING.txt", src=self.SDL2_FOLDER_NAME, dst="LICENSE")

        self.copy("*.h", "include", "%s/include" % self.SDL2_FOLDER_NAME, keep_path=False)

        # Calculate the build directory
        build_dir = self.SDL2_FOLDER_NAME

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
        self.cpp_info.debug.bindirs = [ "bin/Debug" ]
        self.cpp_info.release.libdirs = [ "lib/Release" ]
        self.cpp_info.release.bindirs = [ "bin/Release" ]
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []

        if self.options.sdl2main == True:
            self.cpp_info.libs = ["SDL2", "SDL2main"]
        else:
            self.cpp_info.libs = ["SDL2"]
