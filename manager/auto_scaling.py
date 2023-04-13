import logging
import sched
from sched import scheduler
import time
from aws_utils import AwsUtils
from logger import Logger
from threading import Thread
from typing import Tuple, Any


SCHEDULER_RATE_IN_SECONDS = 60
AUTO_SCALING_SCHEDULER_PRIORITY = 1

aws_utils = AwsUtils()
logger = Logger(logfile='auto_scaling.log') 


def auto_scaling(sc: scheduler) -> None:
    auto_scaling_policy = aws_utils.get_auto_scaling_policy()

    if auto_scaling_policy.enable_auto==1:
        logger.log(f'\nAuto scaling')

        system_cpu_utilization = aws_utils.get_system_cpu_utilization()
        logger.log(f'System cpu utilization: {system_cpu_utilization}')

        logger.log(f'Auto scaling policy: {auto_scaling_policy}')

        worker_pool_lower_bound = aws_utils.get_worker_pool_lower_bound()
        logger.log(f'Worker pool lower bound: {worker_pool_lower_bound}')

        worker_pool_upper_bound = aws_utils.get_worker_pool_upper_bound()
        logger.log(f'Worker pool upper bound: {worker_pool_upper_bound}')

        if system_cpu_utilization == -1:
            logger.log('No workers exist')
            sc.enter(SCHEDULER_RATE_IN_SECONDS, AUTO_SCALING_SCHEDULER_PRIORITY, auto_scaling, (sc,))
            print('running 1')
            return

        workers = [w for w in aws_utils.get_alb_target_group_workers() if w.state == 'healthy']
        workers_count = len(workers)
        logger.log(f'Worker pool count: {workers_count}')

        if system_cpu_utilization > auto_scaling_policy.growth_cpu_threshold:
            workers_count_new = round(workers_count * auto_scaling_policy.expanding_ratio)
            logger.log(f'Grow to worker pool size of: {workers_count_new}')

            if workers_count_new > worker_pool_upper_bound:
                logger.log(f'Unable to grow worker pool to: {workers_count_new} (upper bound = {worker_pool_upper_bound})')
                sc.enter(SCHEDULER_RATE_IN_SECONDS, AUTO_SCALING_SCHEDULER_PRIORITY, auto_scaling, (sc,))
                print('running 2')
                return

            workers_to_launch_count = workers_count_new - workers_count
            logger.log(f'# workers to launch: {workers_to_launch_count}')

            if workers_to_launch_count < 0:
                logger.log(f'Invalid workers_to_launch_count: {workers_to_launch_count}')
                sc.enter(SCHEDULER_RATE_IN_SECONDS, AUTO_SCALING_SCHEDULER_PRIORITY, auto_scaling, (sc,))
                print('running 3')
                return

            for i in range(workers_to_launch_count):
                logger.log(f'Launching ({i + 1} / {workers_to_launch_count}) worker:')
                aws_utils.grow_worker_pool_size_by_1()
                time.sleep(15)

        elif system_cpu_utilization < auto_scaling_policy.shrinking_cpu_threshold:
            workers_count_new = round(workers_count * auto_scaling_policy.shrinking_ratio)
            logger.log(f'Shrink to worker pool size of: {workers_count_new}')

            if workers_count_new < worker_pool_lower_bound:
                logger.log(f'Unable to shrink worker pool to: {workers_count_new} (lower bound = {worker_pool_lower_bound})')
                sc.enter(SCHEDULER_RATE_IN_SECONDS, AUTO_SCALING_SCHEDULER_PRIORITY, auto_scaling, (sc,))
                print('running 4')
                return

            workers_to_terminate_count = workers_count - workers_count_new
            logger.log(f'# workers to terminate: {workers_to_terminate_count}')

            if workers_to_terminate_count < 0:
                logger.log(f'Invalid workers_to_terminate_count: {workers_to_terminate_count}')
                sc.enter(SCHEDULER_RATE_IN_SECONDS, AUTO_SCALING_SCHEDULER_PRIORITY, auto_scaling, (sc,))
                print('running 5')
                return

            for i in range(workers_to_terminate_count):
                logger.log(f'Terminating ({i + 1} / {workers_to_terminate_count}) worker:')
                aws_utils.shrink_worker_pool_size_by_1()
                time.sleep(10)

        else:
            logger.log('No action')

    else:
            logger.log('Auto scaling turned off')

    sc.enter(SCHEDULER_RATE_IN_SECONDS, AUTO_SCALING_SCHEDULER_PRIORITY, auto_scaling, (sc,))


#def run_auto_scaling(*args: Tuple[Any]):
#    logger.log(f'Starting auto scaling thread')
#    sc = sched.scheduler(time.time, time.sleep)
#    sc.enter(SCHEDULER_RATE_IN_SECONDS, AUTO_SCALING_SCHEDULER_PRIORITY, auto_scaling, (sc,))
#    sc.run()



if __name__ == '__main__':
    sc = sched.scheduler(time.time, time.sleep)
    sc.enter(SCHEDULER_RATE_IN_SECONDS, AUTO_SCALING_SCHEDULER_PRIORITY, auto_scaling, (sc,))
    sc.run()

    #thread = Thread(target=run_auto_scaling)
    #thread.start()


