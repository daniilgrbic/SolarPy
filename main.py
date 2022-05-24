import sys
import time

def main():
    start_date = None
    use_horizons = False
    dt = 24  # in hours

    for i in sys.argv:
        arg, *val = i.split("=")
        if arg == "--help" or arg == "-h":
            with open("help.txt", "r") as f:
                print(f.read())
            exit(1)
        if arg == "--start":
            start_date = val[0]
        if arg == "--dt":
            dt = int(val[0])
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
    frame_counter = 0
    simulation_speed = 120  # in days per second
    curr_fps = 30
    min_fps = 30
    max_fps = 40

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
                    simulation_speed = min(simulation_speed + 1, 365)
                else:
                    simulation_speed = max(simulation_speed - 1, 1)
            renderer.handle_events(event)

        renderer.handle_input()

        if not paused:
            if simulation_speed >= min_fps:
                _update_days = simulation_speed // max_fps + int(simulation_speed % max_fps != 0)
                curr_fps = simulation_speed // _update_days
                frame_counter = 0
                for _ in range(_update_days):
                    system.update_rk(dt=dt)
                # print(_update_days, curr_fps, simulation_speed)
            else:
                _skip_days = max_fps // simulation_speed
                curr_fps = simulation_speed * _skip_days
                frame_counter += 1
                if frame_counter >= _skip_days:
                    frame_counter = 0
                    system.update_rk(dt=dt)
                # print(_skip_days, curr_fps, simulation_speed)

        rendered_system = renderer.render(system)
        window.blit(rendered_system, (0, 0))
        pygame.display.flip()

        clock.tick(curr_fps)
        pygame.display.set_caption(f"SolarPy | {system.get_date()} | Speed: {simulation_speed*dt/24:.2f} days/s" +
                                   (" (!)" if clock.get_fps() < curr_fps * 0.8 else "") +
                                   (" | PAUSED" if paused else ""))


if __name__ == '__main__':
    main()
