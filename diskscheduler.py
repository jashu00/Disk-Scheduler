from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

class DiskScheduler:
    def __init__(self, initial_position, max_cylinder=200):
        self.initial_position = initial_position
        self.current_position = initial_position
        self.max_cylinder = max_cylinder
        self.requests = []

    def add_request(self, cylinder):
        if 0 <= cylinder <= self.max_cylinder:
            self.requests.append(cylinder)
        else:
            raise ValueError(f"Request must be between 0 and {self.max_cylinder}")

    def fcfs(self):
        sequence = []
        seek_operations = []
        current = self.initial_position

        for request in self.requests:
            sequence.append(request)
            seek_operations.append(abs(request - current))
            current = request

        total_seek = sum(seek_operations)
        return sequence, total_seek

    def sstf(self):
        sequence = []
        seek_operations = []
        current = self.initial_position
        remaining = self.requests.copy()

        while remaining:
            closest = min(remaining, key=lambda x: abs(x - current))
            sequence.append(closest)
            seek_operations.append(abs(closest - current))
            current = closest
            remaining.remove(closest)

        total_seek = sum(seek_operations)
        return sequence, total_seek

    def scan(self, direction='right'):
        sequence = []
        seek_operations = []
        current = self.initial_position
        remaining = sorted(self.requests.copy())

        if direction == 'right':
            # Requests to the right
            right = [r for r in remaining if r >= current]
            # Requests to the left (reverse order)
            left = sorted([r for r in remaining if r < current], reverse=True)

            # Service right first
            for request in right:
                sequence.append(request)
                seek_operations.append(abs(request - current))
                current = request

            # Go to end if needed
            if right and current != self.max_cylinder:
                sequence.append(self.max_cylinder)
                seek_operations.append(abs(self.max_cylinder - current))
                current = self.max_cylinder

            # Then service left
            for request in left:
                sequence.append(request)
                seek_operations.append(abs(request - current))
                current = request
        else:
            # Requests to the left
            left = sorted([r for r in remaining if r <= current], reverse=True)
            # Requests to the right
            right = sorted([r for r in remaining if r > current])

            # Service left first
            for request in left:
                sequence.append(request)
                seek_operations.append(abs(request - current))
                current = request

            # Go to start if needed
            if left and current != 0:
                sequence.append(0)
                seek_operations.append(abs(0 - current))
                current = 0

            # Then service right
            for request in right:
                sequence.append(request)
                seek_operations.append(abs(request - current))
                current = request

        total_seek = sum(seek_operations)
        return sequence, total_seek

    def cscan(self):
        sequence = []
        seek_operations = []
        current = self.initial_position
        remaining = sorted(self.requests.copy())

        # Requests in the current direction (right)
        right = [r for r in remaining if r >= current]
        # Requests on the other side (left, after wrapping)
        left = [r for r in remaining if r < current]

        # Service right first
        for request in right:
            sequence.append(request)
            seek_operations.append(abs(request - current))
            current = request

        # Go to end and wrap around
        if right:
            sequence.append(self.max_cylinder)
            seek_operations.append(abs(self.max_cylinder - current))
            current = self.max_cylinder

        sequence.append(0)  # Wrap to start
        seek_operations.append(abs(0 - current))
        current = 0

        # Service left requests
        for request in left:
            sequence.append(request)
            seek_operations.append(abs(request - current))
            current = request

        total_seek = sum(seek_operations)
        return sequence, total_seek

class Visualizer:
    def __init__(self, max_cylinder):
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.max_cylinder = max_cylinder
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, max_cylinder)
        self.ax.set_yticks(np.arange(0, max_cylinder + 1, max_cylinder // 10))
        self.ax.grid(True)
        self.head, = self.ax.plot([5], [0], 'ro', markersize=10)  # Disk head
        self.request_points = None

    def init_requests(self, requests):
        if self.request_points:
            self.request_points.remove()
        y = requests
        x = [5] * len(requests)
        self.request_points = self.ax.scatter(x, y, c='blue', alpha=0.5)

    def update_head(self, position):
        self.head.set_data([5], [position])
        self.fig.canvas.draw_idle()

    def animate_sequence(self, sequence, initial_position):
        positions = [initial_position] + sequence

        def update(frame):
            self.update_head(positions[frame])
            return self.head,

        anim = FuncAnimation(self.fig, update, frames=len(positions),
                            interval=500, blit=True)
        plt.title("Disk Head Movement")
        plt.show()
        return anim

def main():
    print("=== Disk Scheduling Simulator ===")
    initial_pos = int(input("Enter initial head position: "))
    max_cylinder = int(input("Enter maximum cylinder number (e.g., 200): "))
    scheduler = DiskScheduler(initial_pos, max_cylinder)

    print("\nEnter disk requests (one per line, empty line to finish):")
    while True:
        req = input("> ")
        if not req:
            break
        try:
            scheduler.add_request(int(req))
        except ValueError as e:
            print(e)

    print("\nAlgorithms available:")
    print("1. FCFS (First-Come-First-Serve)")
    print("2. SSTF (Shortest Seek Time First)")
    print("3. SCAN (Elevator Algorithm)")
    print("4. C-SCAN (Circular SCAN)")
    choice = input("Select algorithm (1-4): ")

    if choice == '1':
        sequence, total_seek = scheduler.fcfs()
        title = "FCFS Scheduling"
    elif choice == '2':
        sequence, total_seek = scheduler.sstf()
        title = "SSTF Scheduling"
    elif choice == '3':
        direction = input("Enter SCAN direction (left/right): ").lower()
        sequence, total_seek = scheduler.scan(direction)
        title = f"SCAN ({direction})"
    elif choice == '4':
        sequence, total_seek = scheduler.cscan()
        title = "C-SCAN Scheduling"
    else:
        print("Invalid choice")
        return

    # Calculate metrics
    avg_seek = total_seek / len(sequence) if sequence else 0

    print("\n=== Results ===")
    print(f"Algorithm: {title}")
    print(f"Service sequence: {sequence}")
    print(f"Total seek time: {total_seek}")
    print(f"Average seek time: {avg_seek:.2f}")

    # Visualization
    if input("\nShow visualization? (y/n): ").lower() == 'y':
        visualizer = Visualizer(max_cylinder)
        visualizer.init_requests(scheduler.requests)
        visualizer.animate_sequence(sequence, initial_pos)

if __name__ == "__main__":
    main()
