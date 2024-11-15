#!/usr/bin/env python3
import tkinter as tk
from tkinter import messagebox
import rospy
from sensor_msgs.msg import NavSatFix

class GPSInputApp:
    def __init__(self, master):
        self.master = master
        master.title("GPS Waypoints Input")

        # Initialize ROS node
        rospy.init_node('gps_gui', anonymous=True)
        self.publisher = rospy.Publisher('/gps_goal_fix', NavSatFix, queue_size=10)

        # Title
        title_font = ("Helvetica", 16, "bold")
        tk.Label(master, text="GPS Waypoints Input", font=title_font).grid(row=0, column=0, columnspan=8, pady=10)

        # Number of Waypoints
        tk.Label(master, text="Number of Waypoints", font=("Helvetica", 12, "bold")).grid(row=1, column=0, columnspan=8, pady=5)
        self.num_waypoints = tk.Entry(master)
        self.num_waypoints.grid(row=2, column=0, columnspan=8)

        # Waypoints Entry
        self.waypoints_frame = tk.Frame(master)
        self.waypoints_frame.grid(row=3, column=0, columnspan=8)

        # Button to create waypoint entry fields
        self.create_waypoints_button = tk.Button(master, text="Create Waypoints Entry", command=self.create_waypoints_entry_fields)
        self.create_waypoints_button.grid(row=4, column=0, columnspan=8, pady=10)

        # Submit Button
        self.submit_button = tk.Button(master, text="Submit", command=self.update_gps)
        self.submit_button.grid(row=5, column=0, columnspan=8, pady=10)

    def create_waypoints_entry_fields(self):
        num_waypoints_str = self.num_waypoints.get()

        # Check if the entry field is empty
        if not num_waypoints_str:
            # Display an error message to the user
            messagebox.showerror("Error", "Please enter the number of waypoints.")
            return

        try:
            # Convert the number of waypoints to an integer
            num_waypoints = int(num_waypoints_str)
        except ValueError:
            # Display an error message if the input is not a valid integer
            messagebox.showerror("Error", "Please enter a valid number of waypoints.")
            return

        # Clear previous entry fields
        for widget in self.waypoints_frame.winfo_children():
            widget.destroy()

        self.waypoints_entries = []

        for i in range(num_waypoints):
            tk.Label(self.waypoints_frame, text=f"Waypoint {i+1}", font=("Helvetica", 12, "bold")).grid(row=i, column=0, pady=5)

            # Latitude
            tk.Label(self.waypoints_frame, text="Latitude").grid(row=i, column=1)
            lat_entry = tk.Entry(self.waypoints_frame)
            lat_entry.grid(row=i, column=2)

            # Longitude
            tk.Label(self.waypoints_frame, text="Longitude").grid(row=i, column=3)
            lon_entry = tk.Entry(self.waypoints_frame)
            lon_entry.grid(row=i, column=4)

            self.waypoints_entries.append((lat_entry, lon_entry))

    def update_gps(self):
        try:
            # Number of Waypoints
            num_waypoints_str = self.num_waypoints.get()

            # Check if the entry field is empty
            if not num_waypoints_str:
                # Display an error message to the user
                messagebox.showerror("Error", "Please enter the number of waypoints.")
                return

            num_waypoints = int(num_waypoints_str)

            # Waypoints
            waypoints = []
            for i in range(num_waypoints):
                lat = float(self.waypoints_entries[i][0].get())
                lon = float(self.waypoints_entries[i][1].get())
                waypoints.append((lat, lon))

            # Publish waypoints
            self.publish_waypoints(waypoints)

            # Clear entry fields
            self.num_waypoints.delete(0, tk.END)
            for i in range(num_waypoints):
                for entry in self.waypoints_entries[i]:
                    entry.delete(0, tk.END)

            # Provide feedback to the user
            messagebox.showinfo("Success", "Waypoints published successfully.")

        except ValueError as e:
            # Handle conversion errors
            messagebox.showerror("Error", str(e))

    def publish_waypoints(self, waypoints):
        # Publish waypoints
        for lat, lon in waypoints:
            waypoint_msg = NavSatFix()
            waypoint_msg.latitude = lat
            waypoint_msg.longitude = lon
            self.publisher.publish(waypoint_msg)

            # Optionally, you can add some delay between publishing waypoints to simulate traveling time
            rospy.sleep(1)

            # You can also print or display the published waypoints if needed
            print(f"Published waypoint: Latitude {lat}, Longitude {lon}")

if __name__ == '__main__':
    root = tk.Tk()
    app = GPSInputApp(root)
    root.mainloop()

