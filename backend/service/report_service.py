from sqlalchemy import func, desc, case
from database.session import db_session as db
from database.model import Trek, Booking, User, Role, BookingStatus, staff_trek_association

from datetime import date, datetime, timedelta


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
    

    def generate_monthly_report():
        
        today = date.today()
        thirty_days_ago = today - timedelta(days=30)
        month_name = today.strftime('%B %Y')

        try:
            total_trekkers = db.query(User).filter(User.role == Role.TREKKER).count()
            
            new_trekkers = db.query(User).filter(
                User.role == Role.TREKKER,
                User.date_created >= thirty_days_ago
            ).count()

            total_treks = db.query(Trek).count()

            # bookings in last 30 days (complete and paid)
            recent_bookings = db.query(Booking).filter(
                Booking.booking_date >= thirty_days_ago,
                Booking.status == BookingStatus.COMPLETED,
                Booking.payment_status == True
            ).all()

            total_completed_bookings = len(recent_bookings)

            trek_status = {}
            total_revenue = 0

            for booking in recent_bookings:
                trek_id = booking.trek_id
                if trek_id not in trek_status:
                    trek_status[trek_id] = {
                        "name": booking.trek.trek_name, 
                        "bookings": 0,
                        "revenue": 0
                    }
                
                # calculate revenue: Price * number of people booked 
                revenue = booking.trek.price * booking.number_of_booking 

                trek_status[trek_id]["bookings"] += booking.number_of_booking
                trek_status[trek_id]["revenue"] += revenue
                total_revenue += revenue

            popular_treks = sorted(trek_status.values(), key=lambda x: x["bookings"], reverse=True)
            status_counts = db.query(Trek.status, func.count(Trek.trek_id)).group_by(Trek.status).all()

        except Exception as e:
            print(f"Database error during reprot generation: {e}")
            return


        status_html = ""
        for status, count in status_counts:
            status_html += f"""
                <tr>
                    <td style='padding: 10px; border-bottom: 1px solid #e5e7eb; color: #4b5563;'>{status.name}</td>
                    <td style='padding: 10px; border-bottom: 1px solid #e5e7eb; font-weight: 600; color: #111827;'>{count}</td>
                </tr>
            """

        popular_html = ""
        if popular_treks:
            for i, t in enumerate(popular_treks):
                popular_html += f"""
                <tr>
                    <td style='padding: 10px; border-bottom: 1px solid #e5e7eb; color: #4b5563;'>#{i+1} {t['name']}</td>
                    <td style='padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: center; font-weight: 600; color: #111827;'>{t['bookings']}</td>
                    <td style='padding: 10px; border-bottom: 1px solid #e5e7eb; text-align: right; font-weight: 600; color: #1a6b42;'>₹ {t['revenue']:,.2f}</td>
                </tr>
            """
        else:
            popular_html = """<tr>
                <td colspan='3' style='padding: 15px; text-align: center; color: #6b7280; font-style: italic;'>No completed bookings recorded in the last 30 days.</td>
            </tr>
        """
                
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"></head>
            <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f3f4f6; padding: 20px; margin: 0;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                        
                    <div style="background-color: #1a6b42; padding: 25px 20px; text-align: center;">
                        <h2 style="color: #ffffff; margin: 0; font-size: 22px;">Monthly Performance Report</h2>
                        <p style="color: #a7f3d0; margin: 5px 0 0 0; font-size: 14px;">{month_name}</p>
                    </div>

                    <div style="padding: 30px 20px;">
                        <h3 style="color: #111827; font-size: 16px; margin-top: 0; border-bottom: 2px solid #1a6b42; padding-bottom: 8px; display: inline-block;">1. Executive Summary</h3>
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px; background: #f9fafb; border-radius: 6px;">
                            <tr>
                                <td style="padding: 12px 15px; color: #4b5563;">Total Trekkers</td>
                                <td style="padding: 12px 15px; text-align: right; font-weight: bold; color: #111827;">{total_trekkers}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 15px; color: #4b5563;">New Signups (30 Days)</td>
                                <td style="padding: 12px 15px; text-align: right; font-weight: bold; color: #1a6b42;">+{new_trekkers}</td>
                            </tr>
                            <tr>
                                <td style="padding: 12px 15px; color: #4b5563;">Completed Bookings</td>
                                <td style="padding: 12px 15px; text-align: right; font-weight: bold; color: #111827;">{total_completed_bookings}</td>
                            </tr>
                            <tr style="background: #eef2ff;">
                                    <td style="padding: 12px 15px; color: #3730a3; font-weight: bold;">Total Revenue</td>
                                    <td style="padding: 12px 15px; text-align: right; font-weight: bold; color: #3730a3; font-size: 16px;">₹ {total_revenue:,.2f}</td>
                            </tr>
                        </table>

                        <h3 style="color: #111827; font-size: 16px; border-bottom: 2px solid #1a6b42; padding-bottom: 8px; display: inline-block;">2. Top Treks by Bookings</h3>
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 30px;">
                            <thead>
                                <tr>
                                    <th style="text-align: left; padding: 10px; background: #f3f4f6; color: #6b7280; font-size: 12px; text-transform: uppercase;">Trek Name</th>
                                    <th style="text-align: center; padding: 10px; background: #f3f4f6; color: #6b7280; font-size: 12px; text-transform: uppercase;">Bookings</th>
                                    <th style="text-align: right; padding: 10px; background: #f3f4f6; color: #6b7280; font-size: 12px; text-transform: uppercase;">Revenue</th>
                                </tr>
                            </thead>
                            <tbody>
                                    {popular_html}
                            </tbody>
                        </table>

                        <h3 style="color: #111827; font-size: 16px; border-bottom: 2px solid #1a6b42; padding-bottom: 8px; display: inline-block;">3. Platform Trek Status</h3>
                        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                            {status_html}
                        </table>
                    </div>
                </div>
            </body>
            </html>
        """

        return html_content
            



