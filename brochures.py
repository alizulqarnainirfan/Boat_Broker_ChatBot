from fpdf import FPDF
from fastapi.responses import FileResponse
import os
from db import get_connection
import mysql.connector
from fastapi import HTTPException

def generate_brochure(boat_name: str):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM brochures WHERE name = %s", (boat_name,))
        data = cursor.fetchone()

        if not data:
            raise HTTPException(status_code=404, detail="Brochure data not found. Please fill it from the Admin panel")

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", 'B', 16)

        # Title
        pdf.cell(0, 10, f"{data['name']} £{data['amount']}", ln=True, align='C')

        def section(title):
            pdf.ln(5)
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, title, ln=True)
            pdf.set_font("Arial", '', 12)

        def field(label, value):
            if value not in [None, "None", "null", ""]:
                pdf.cell(80, 8, f"{label}:", border=0)
                pdf.cell(0, 8, str(value), ln=True)

        # --- Sections ---
        section("Basic Info")
        field("Length/beam", data["length"])
        field("No. of berths", data["no_of_berths"])
        field("Stern type", data["stern_type"])
        field("Engine", data["engine"])
        field("Hull builder", data["hull_builder"])
        field("Last service", data["last_service"])
        field("Fit out", data["fit_out"])
        field("Blacking", data["blacking"])
        field("Year", data["year"])
        field("Boat safety", data["boat_safety"])
        field("Steel spec", data["steel_spec"])
        field("Recent survey", data["recent_survey"])

        section("History")
        for key in ["cin_number", "crt_number", "licence_number", "no_of_owners", "engine_service_history", "boiler_service_history", "survey", "anodes", "documentation_available"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Engine Specs")
        for key in ["engine_hours", "engine_gearbox", "engine_bow_thruster", "engine_weed_hatch", "diesel_tank_capacity", "engine_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Dimensions")
        for key in ["draft", "internal_headroom", "saloon", "galley", "bathroom", "bedroom"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Heating & Hot Water")
        for key in ["central_heating", "solid_fuel_stove", "source_of_hot_water", "water_tank", "water_tank_capacity", "heating_system_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Electrical System")
        for key in ["alternator", "batteries", "lighting", "inverter_charger", "landline_socket", "generator", "electrical_system_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Gas System")
        for key in ["gas_bottles", "appliances", "gas_system_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Cabin Fitout")
        for key in ["insulation", "ballast", "ceiling", "cabin_sides", "hull_sides", "flooring", "side_doors", "windows", "cabin_fit_out_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Galley")
        for key in ["cooker", "fridge_freezer", "microwave", "washing_machine", "galley_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Bathroom")
        for key in ["toilet", "waste_tank_capacity", "bath_shower", "vanity_basin", "bathroom_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Bedroom")
        for key in ["bed", "dinette", "bedroom_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        section("Other")
        for key in ["tv", "covers", "navigation_equipment", "other_extras"]:
            field(key.replace("_", " ").title(), data.get(key))

        # Footer Disclaimer
        pdf.ln(10)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 8, """For further information, arrange a viewing or make an offer, please call Noel on 07960 768724

PLEASE NOTE: The Boat Brokers are acting as Brokers only. Whilst every care has been taken in their preparation, the correctness of these particulars is not guaranteed. They do not form part of any current or future contract. Prospective purchasers are advised to have an independent survey carried out by a qualified marine surveyor prior to completion of purchase.

The Boat Brokers is a trading name of Creary Holdings Ltd. Company no: 14876430
""")

        # Save and return
        filename = f"brochure_vendor_{boat_name}.pdf"
        filepath = f"./{filename}"
        pdf.output(filepath)

        return FileResponse(filepath, media_type="application/pdf", filename=filename)

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=str(err))

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()





























# from fastapi import APIRouter, HTTPException
# from fastapi.responses import FileResponse
# from db import get_connection
# from fpdf import FPDF
# import mysql.connector
# import os

# # router = APIRouter()

# # @router.get("/brochure/{boat_name}")
# def generate_brochure(boat_name: str):
#     try:
#         # Connect to the database
#         conn = get_connection()
#         cursor = conn.cursor(dictionary=True)

#         # Fetch brochure data for the vendor
#         cursor.execute("SELECT * FROM brochures WHERE name = %s", (boat_name,))
#         brochure_data = cursor.fetchone()

#         if not brochure_data:
#             raise HTTPException(status_code=404, detail="Brochure data not found. Please fill it from the Admin panel")

#         # Generate PDF
#         pdf = FPDF()
#         pdf.add_page()
#         pdf.set_font("Arial", size=12)

#         # Add content
#         pdf.cell(200, 10, txt=f"Brochure for BOAT : {boat_name}", ln=True, align='C')
#         for key, value in brochure_data.items():
#             pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)

#         # Save to file
#         filename = f"brochure_vendor_{boat_name}.pdf"
#         filepath = f"./{filename}"
#         pdf.output(filepath)

#         return FileResponse(filepath, media_type="application/pdf", filename=filename)

#     except mysql.connector.Error as err:
#         raise HTTPException(status_code=500, detail=str(err))

#     finally:
#         if conn.is_connected():
#             cursor.close()
#             conn.close()
