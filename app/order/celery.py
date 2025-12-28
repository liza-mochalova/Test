from celery import Celery
import random
import time
from sqlalchemy.orm import Session
from database import SessionLocal, OrderOrm, ReagentsOrm, OrderStatus
from datetime import datetime, timezone
import logging

from order.schemas import Priority

celery = Celery(
    'lab',
    broker='redis://127.0.0.1:6379/0',
    backend='redis://127.0.0.1:6379/0',
    broker_connection_retry_on_startup=True
)

celery.conf.update(
    task_default_priority=5,
    task_queue_max_priority=10,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

PRIORITY_MAPPING = {
    Priority.LOW: 1,
    Priority.NORMAL: 5,
    Priority.HIGH: 10,
}
logger = logging.getLogger(__name__)

@celery.task(bind=True)
def produce_reagent(self, order_id: int):
    logger.info(f"Starting production for order {order_id}")
    
    db = SessionLocal()
    try:
        order = db.query(OrderOrm).filter(OrderOrm.id == order_id).first()
        if not order or order.status != OrderStatus.IN_PROGRESS:
            return
        logger.info(f"Processing order {order_id} with priority: {order.priority}")
        self.update_state(
            state='PROGRESS',
            meta={'order_id': order_id, 'status': 'started'}
        )
        # Симуляция производства
        base_time_per_unit = random.uniform(15, 30)
        
        if order.priority == Priority.HIGH:
            time_per_unit = base_time_per_unit * 0.9
        elif order.priority == Priority.LOW:
            time_per_unit = base_time_per_unit * 1.1
        else:
            time_per_unit = base_time_per_unit
        
        total_time = time_per_unit * order.quantity
        success = random.random() < 0.8
        
        if success:
            order.status = OrderStatus.COMPLETED
            reagent = db.query(ReagentsOrm).filter(ReagentsOrm.id == order.reagent_id).first()
            if reagent:
                reagent.quantity += order.quantity
            order.result_comment = "Production successful"
            logger.info(f"Order {order_id} completed")
        else:
            order.status = OrderStatus.FAILED
            order.result_comment = "Production failed: batch defect"
            final_task_state = 'FAILURE'
            logger.warning(f"Order {order_id} failed")
        
        order.completed_at = datetime.datetime.now(timezone.utc)
        db.commit()
        
        self.update_state(
            state=final_task_state,
            meta={
                'order_id': order_id,
                'status': order.status.value,
                'result': order.result_comment
            }
        )

    except Exception as e:
        logger.error(f"Error in production task: {e}")
        db.rollback()
    finally:
        db.close()