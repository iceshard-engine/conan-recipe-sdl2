newoption {
    trigger = "shared",
    description = "Build as shared lib",
}

newoption {
    trigger = "arch",
    description = "Build for the given architecture",
    value = "ARCH"
}

workspace "SDL2"
    configurations { "Debug", "Release" }

    architecture(_OPTIONS.arch)

    filter { "action:vs*" }
        defines { "_CRT_SECURE_NO_WARNINGS" }

    filter { "Debug" }
        symbols "On"

    filter { "Release" }
        optimize "On"

    project "SDL2"
        kind(iif(_OPTIONS.shared, "SharedLib", "StaticLib"))
        language "C"

        includedirs {
            "src",
            "include"
        }

        files {
            "src/**.c"
        }

        filter { "kind:SharedLib" }
            defines { "SDL2_BUILD_AS_DLL" }
