import sys
import time


def main():
    start_date = None
    use_horizons = False

    for i in sys.argv:
        arg, *val = i.split("=")
        if arg == "--help" or arg == "-h":
            with open("help.txt", "r") as f:
                print(f.read())
            exit(1)
        if arg == "--start":
            start_date = val[0]
        if arg == "--horizons":
            use_horizons = True

    if not start_date:
        localtime = time.localtime()
        start_date = f"{localtime.tm_year}-{localtime.tm_mon}-{localtime.tm_mday}"

    import os
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
    import pygame
    pygame.init()
    window = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
    clock = pygame.time.Clock()

    from solarsystem import SolarSystem
    system = SolarSystem(
        start_date=start_date,
        use_horizons=use_horizons
    )

    from renderer import Renderer
    renderer = Renderer()

    paused = True
    frame = 0
    simulation_speed = 30
    max_fps = 90

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                system.dump_state()
                print(f"Dumped state for {system.get_date()}")
            if event.type == pygame.MOUSEWHEEL and pygame.mouse.get_pressed()[2]:
                if event.y > 0:
                    simulation_speed = min(simulation_speed + 1, max_fps)
                else:
                    simulation_speed = max(simulation_speed - 1, 1)
            renderer.handle_events(event)

        renderer.handle_input()

        if not paused:
            if frame >= max_fps / simulation_speed:
                system.update_rk()
                frame = 0

        rendered_system = renderer.render(system)
        window.blit(rendered_system, (0, 0))
        pygame.display.flip()
        pygame.display.set_caption(f"SolarPy | {system.get_date()} | Speed: {simulation_speed} days/s")

        clock.tick(max_fps)
        frame += 1


if __name__ == '__main__':
    main()
