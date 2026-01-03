from collections import deque

from common.Utils import main
from day10.Utils import Indicator, Button, LightsParser


class LeastButtonPressFinder:

    @staticmethod
    def run(input_toggles: list[tuple[Indicator, list[Button]]]) -> int:
        presses = 0

        for indicator, buttons in input_toggles:
            presses += LeastButtonPressFinder._find_presses(indicator, buttons)

        return presses

    @staticmethod
    def _find_presses(target_indicator: Indicator, buttons: list[Button]) -> int:
        press = 0
        if target_indicator.all_false():
            return press

        target_size = target_indicator.get_size()
        start_indicator = Indicator(target_size)
        queue = deque([(start_indicator, 0)])
        seen = {start_indicator}

        while queue:
            indicator, press = queue.popleft()
            if indicator == target_indicator:
                break

            for button in buttons:
                n_indicator = indicator.press_button(button)
                if n_indicator not in seen:
                    queue.append((n_indicator, press + 1))
                    seen.add(n_indicator)

        return press


if __name__ == "__main__":
    main(LightsParser, LeastButtonPressFinder, test=False)
