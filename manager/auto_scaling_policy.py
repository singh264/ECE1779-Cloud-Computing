class AutoScalingPolicy:
    def __init__(self, growth_cpu_threshold: float, shrinking_cpu_threshold: float,
                    expanding_ratio: float, shrinking_ratio: float, enable_auto: int) -> None:
        self.__growth_cpu_threshold = growth_cpu_threshold
        self.__shrinking_cpu_threshold = shrinking_cpu_threshold
        self.__expanding_ratio = expanding_ratio
        self.__shrinking_ratio = shrinking_ratio
        self.__enable_auto = enable_auto
    
    @property
    def growth_cpu_threshold(self) -> float:
        return self.__growth_cpu_threshold
    
    @property
    def shrinking_cpu_threshold(self) -> float:
        return self.__shrinking_cpu_threshold
    
    @property
    def expanding_ratio(self) -> float:
        return self.__expanding_ratio
    
    @property
    def shrinking_ratio(self) -> float:
        return self.__shrinking_ratio

    @property
    def enable_auto(self) -> int:
        return self.__enable_auto

    def __str__(self) -> str:
        return f'''(growth cpu threshold = {self.growth_cpu_threshold}, 
                        shrinking cpu threshold = {self.shrinking_cpu_threshold}, 
                        expanding ratio = {self.expanding_ratio}
                        shrinking ratio = {self.shrinking_ratio}
                        enable_auto = {self.enable_auto})'''
