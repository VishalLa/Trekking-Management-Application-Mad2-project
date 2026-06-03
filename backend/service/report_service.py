from sqlalchemy import func, desc, case
from database.session import db_session as db
from database.model import Trek, Booking, User, Role, staff_trek_association


class ReportService:

    @staticmethod
    def get_dashboard_stats():

        total_treks = db.query(func.count(Trek.trek_id)).scalar() or 0
        total_bookings = db.query(func.count(Booking.booking_id)).scalar() or 0

        raw_trek_status = db.query(Trek.status, func.count(Trek.trek_id)).group_by(Trek.status).all()
        trek_status_counts = {status.name: count for status, count in raw_trek_status}

        raw_booking_status = db.query(Booking.status, func.count(Booking.booking_id)).group_by(Booking.status).all()
        booking_status_counts = {status.name: count for status, count in raw_booking_status}

        raw_difficulty = db.query(Trek.difficulty, func.count(Trek.trek_id)).group_by(Trek.difficulty).all()
        difficulty_counts = {diff.name: count for diff, count in raw_difficulty}

        raw_trek_performance = db.query(
            Trek.trek_id,
            Trek.trek_name,
            func.count(Booking.booking_id).label("total_bookings"),
            func.sum(
                case(
                    (Booking.payment_status == True, Trek.price * Booking.number_of_booking), 
                    else_=0
                )
            ).label("revenue")
        ).outerjoin(Booking, Trek.trek_id == Booking.trek_id).group_by(Trek.trek_id, Trek.trek_name).all()

        trek_performance = [
            {
                "id": t.trek_id,
                "name": t.trek_name,
                "total_bookings": t.total_bookings,
                "total_revenue": round(t.revenue or 0.0, 2)
            } for t in raw_trek_performance
        ]

        top_revenue_treks = sorted(trek_performance, key=lambda x: x["total_revenue"], reverse=True)[:5]
        grand_total_revenue = sum(t["total_revenue"] for t in trek_performance)


        total_trekkers = db.query(func.count(User.id)).filter(User.role == Role.TREKKER).scalar() or 0
        total_staff = db.query(func.count(User.id)).filter(User.role == Role.STAFF).scalar() or 0

        total_assignments = db.query(func.count(staff_trek_association.c.staff_id)).scalar() or 0
        avg_staff_per_trek = round(total_assignments / total_treks, 1) if total_treks > 0 else 0.0


        return {
            "platform_overview": {
                "total_revenue": grand_total_revenue,
                "total_bookings": total_bookings,
                "total_treks": total_treks,
            },
            "trek_metrics": {
                "by_status": trek_status_counts,
                "by_difficulty": difficulty_counts,
                "average_staff_per_trek": avg_staff_per_trek,
                "top_5_revenue_generators": top_revenue_treks,
                "all_trek_performance": trek_performance
            },
            "booking_metrics": {
                "by_status": booking_status_counts,
            },
            "user_metrics": {
                "total_trekkers": total_trekkers,
                "total_staff": total_staff,
                "total_assignments": total_assignments
            }
        }

