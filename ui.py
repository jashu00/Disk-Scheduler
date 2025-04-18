import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

class DiskScheduler:
    def __init__(self, initial_position, max_cylinder=200):
        self.initial_position = initial_position
        self.max_cylinder = max_cylinder
        self.requests = []

    def add_request(self, cylinder):
        if 0 <= cylinder <= self.max_cylinder:
            self.requests.append(cylinder)
        else:
            raise ValueError(f"Request must be between 0 and {self.max_cylinder}")

    def fcfs(self):
        sequence = self.requests.copy()
        current = self.initial_position
        total_seek = 0
        seek_operations = []
        
        for request in sequence:
            seek_operations.append(abs(request - current))
            current = request
            
        total_seek = sum(seek_operations)
        return sequence, total_seek

    def sstf(self):
        if not self.requests:
            return [], 0
            
        sequence = []
        total_seek = 0
        current = self.initial_position
        remaining = self.requests.copy()
        
        while remaining:
            closest = min(remaining, key=lambda x: abs(x - current))
            seek = abs(closest - current)
            total_seek += seek
            current = closest
            sequence.append(closest)
            remaining.remove(closest)
            
        return sequence, total_seek

    def scan(self, direction='right'):
        if not self.requests:
            return [], 0
            
        sequence = []
        total_seek = 0
        current = self.initial_position
        remaining = sorted(self.requests.copy())
        
        if direction == 'right':
            right = [r for r in remaining if r >= current]
            left = sorted([r for r in remaining if r < current], reverse=True)
            
            for req in right:
                sequence.append(req)
                total_seek += abs(req - current)
                current = req
                
            if right and current != self.max_cylinder:
                sequence.append(self.max_cylinder)
                total_seek += abs(self.max_cylinder - current)
                current = self.max_cylinder
                
            for req in left:
                sequence.append(req)
                total_seek += abs(req - current)
                current = req
        else:
            left = sorted([r for r in remaining if r <= current], reverse=True)
            right = sorted([r for r in remaining if r > current])
            
            for req in left:
                sequence.append(req)
                total_seek += abs(req - current)
                current = req
                
            if left and current != 0:
                sequence.append(0)
                total_seek += abs(0 - current)
                current = 0
                
            for req in right:
                sequence.append(req)
                total_seek += abs(req - current)
                current = req
                
        return sequence, total_seek

    def cscan(self):
        if not self.requests:
            return [], 0
            
        sequence = []
        total_seek = 0
        current = self.initial_position
        remaining = sorted(self.requests.copy())
        
        right = [r for r in remaining if r >= current]
        left = [r for r in remaining if r < current]
        
        for req in right:
            sequence.append(req)
            total_seek += abs(req - current)
            current = req
            
        if right:
            sequence.append(self.max_cylinder)
            total_seek += abs(self.max_cylinder - current)
            current = self.max_cylinder
            
        sequence.append(0)
        total_seek += abs(0 - current)
        current = 0
        
        for req in left:
            sequence.append(req)
            total_seek += abs(req - current)
            current = req
            
        return sequence, total_seek

def plot_movement(sequence, initial_pos, max_cylinder, requests):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_title("Disk Head Movement")
    ax.set_ylabel("Cylinder Number")
    ax.set_xlabel("Time Step")
    ax.set_ylim(0, max_cylinder)
    ax.grid(True)
    
    # Plot requests
    ax.scatter([0]*len(requests), requests, c='blue', alpha=0.5, label='Requests')
    
    # Plot head movement
    x = list(range(len(sequence)+1))
    y = [initial_pos] + sequence
    ax.plot(x, y, 'ro-', markersize=6, label='Head Movement')
    
    # Annotate positions
    for i, (xi, yi) in enumerate(zip(x, y)):
        if i == 0:
            ax.annotate(f'Start: {yi}', (xi, yi), 
                       textcoords="offset points", xytext=(0,10), ha='center')
        else:
            ax.annotate(str(yi), (xi, yi), 
                       textcoords="offset points", xytext=(0,5), ha='center')
    
    ax.legend()
    return fig

def main():
    st.set_page_config(page_title="Disk Scheduling Simulator", layout="wide")
    st.title("Disk Scheduling Simulator")
    
    # Initialize session state
    if 'requests' not in st.session_state:
        st.session_state.requests = []
    
    # Input parameters
    col1, col2 = st.columns(2)
    with col1:
        initial_pos = st.number_input("Initial Head Position", 
                                    min_value=0, value=50, step=1)
    with col2:
        max_cylinder = st.number_input("Maximum Cylinder", 
                                     min_value=1, value=200, step=1)
    
    # Request management
    st.subheader("Request Management")
    req_col1, req_col2 = st.columns([3, 1])
    with req_col1:
        new_request = st.number_input("Add New Request", 
                                     min_value=0, max_value=max_cylinder, step=1)
    with req_col2:
        st.markdown("##")
        if st.button("Add Request", use_container_width=True):
            st.session_state.requests.append(new_request)
    
    st.write(f"Current Requests: {st.session_state.requests}")
    
    if st.button("Clear All Requests", type="secondary"):
        st.session_state.requests = []
        st.experimental_rerun()
    
    # Algorithm selection
    st.subheader("Algorithm Configuration")
    algorithm = st.selectbox("Scheduling Algorithm", 
                           ["FCFS", "SSTF", "SCAN", "C-SCAN"])
    
    scan_direction = "right"
    if algorithm == "SCAN":
        scan_direction = st.radio("SCAN Direction", ["left", "right"], horizontal=True)
    
    # Run simulation
    if st.button("Run Simulation", type="primary"):
        if not st.session_state.requests:
            st.error("Please add at least one request!")
            return
            
        try:
            scheduler = DiskScheduler(initial_pos, max_cylinder)
            for req in st.session_state.requests:
                scheduler.add_request(req)
            
            if algorithm == "FCFS":
                sequence, total_seek = scheduler.fcfs()
            elif algorithm == "SSTF":
                sequence, total_seek = scheduler.sstf()
            elif algorithm == "SCAN":
                sequence, total_seek = scheduler.scan(scan_direction)
            elif algorithm == "C-SCAN":
                sequence, total_seek = scheduler.cscan()
            
            # Display results
            st.subheader("Results")
            results_col1, results_col2 = st.columns(2)
            
            with results_col1:
                st.metric("Total Seek Time", f"{total_seek} cylinders")
                st.metric("Average Seek Time", f"{total_seek/len(sequence):.2f} cylinders")
            
            with results_col2:
                st.write("**Access Sequence:**")
                st.code(f"{sequence}")
            
            # Show visualization
            st.subheader("Visualization")
            fig = plot_movement(sequence, initial_pos, max_cylinder, st.session_state.requests)
            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"Simulation Error: {str(e)}")

if __name__ == "__main__":
    main()