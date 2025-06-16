from escpos.printer import Usb
import usb.backend.libusb1 as libusb1
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import base64
from io import BytesIO
from PIL import Image
import requests

# Configure libusb backend
backend = libusb1.get_backend(
    find_library=lambda x: r"C:\libusb\MinGW64\dll\libusb-1.0.dll"
)

# Replace with your VID/PID and endpoints
PRINTER_CONFIG = {
    "idVendor": 0x0416,  # VID
    "idProduct": 0x5011,  # PID
    "in_ep": 0x81,  # Input endpoint
    "out_ep": 0x01,  # Output endpoint
}


class PrintImageView(APIView):
    def post(self, request):
        # Check if the request contains 'is_sales_report'

        # Get image data from the request
        image_data = request.data.get("image_data")  # Base64-encoded string
        image_url = request.data.get("image_url")  # URL of the image

        if not image_data and not image_url:
            return Response(
                {"error": "Please provide either 'image_data' or 'image_url'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Load the image from Base64 or URL
            if image_data:
                # Remove the "data:image/png;base64," prefix if present
                if image_data.startswith("data:image/"):
                    image_data = image_data.split(",")[1]

                # Decode Base64 image
                try:
                    image = Image.open(BytesIO(base64.b64decode(image_data)))
                except Exception as e:
                    return Response(
                        {"error": f"Failed to decode Base64 image: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                # Download image from URL
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content))
                except Exception as e:
                    return Response(
                        {"error": f"Failed to download image from URL: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            # Resize the image to fit the printer's width
            printer_width = 384  # For 58mm printers
            aspect_ratio = image.height / image.width
            new_height = int(printer_width * aspect_ratio)
            resized_image = image.resize(
                (printer_width, new_height), Image.Resampling.LANCZOS
            )

            # Convert the image to black and white
            # resized_image = resized_image.convert('1')

            # Initialize the printer
            try:
                # printer = Usb(
                #     idVendor=PRINTER_CONFIG["idVendor"],
                #     idProduct=PRINTER_CONFIG["idProduct"],
                #     in_ep=PRINTER_CONFIG["in_ep"],
                #     out_ep=PRINTER_CONFIG["out_ep"],
                #     backend=backend
                # )
                # Initialize the printer
                printer = Usb(
                    idVendor=PRINTER_CONFIG["idVendor"],
                    idProduct=PRINTER_CONFIG["idProduct"],
                    in_ep=PRINTER_CONFIG["in_ep"],
                    out_ep=PRINTER_CONFIG["out_ep"],
                    backend=backend,
                )

                # ✅ Check if the printer profile exists
                if hasattr(printer, "profile") and hasattr(printer.profile, "media"):
                    printer.profile.media["width"]["pixel"] = 384  # Set width manually
                else:
                    print("⚠️ Printer profile or media width is missing!")
            except Exception as e:
                return Response(
                    {"error": f"Failed to initialize printer: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Print the image
            try:
                printer.image(resized_image)
                printer.cut()
            except Exception as e:
                return Response(
                    {"error": f"Failed to print image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"message": "Image printed successfully!"}, status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
