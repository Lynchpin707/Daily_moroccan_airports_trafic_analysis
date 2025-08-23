import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

# Create outputs directory if it doesn't exist
os.makedirs('./outputs/', exist_ok=True)

# Set style for professional, minimalist visualizations
plt.style.use('default')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9

# Define neutral, professional color palette
colors = {
    'primary': '#2E4057',    # Dark blue-gray
    'secondary': '#048A81',  # Teal
    'accent': '#54C6EB',     # Light blue
    'neutral': '#9DA5B4',    # Gray
    'success': '#06D6A0',    # Green
    'warning': '#FFD23F',    # Yellow
    'danger': '#EE6352'      # Red
}

class MoroccoAirportAnalysis:
    """
    Comprehensive business analysis for Morocco's top 5 airports flight data
    """
    
    def __init__(self, df):
        self.df = df.copy()
        self.report_lines = []
        self.prepare_data()
        
    def prepare_data(self):
        """Clean and prepare data for analysis"""
        # Convert timestamp columns
        timestamp_cols = ['scheduled', 'estimated', 'actual', 'data_timestamp']
        for col in timestamp_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
        
        # Create derived metrics
        self.df['delay_minutes'] = (self.df['actual'] - self.df['scheduled']).dt.total_seconds() / 60
        self.df['is_delayed'] = self.df['delay_minutes'] > 15  # Industry standard
        self.df['is_cancelled'] = self.df['status'].str.lower().str.contains('cancel', na=False)
        self.df['hour'] = self.df['scheduled'].dt.hour
        self.df['day_of_week'] = self.df['scheduled'].dt.day_name()
        self.df['month'] = self.df['scheduled'].dt.month_name()
        
        # Identify domestic vs international flights
        self.df['flight_category'] = np.where(
            self.df['origin_country'] == self.df['destination_country'], 
            'Domestic', 'International'
        )
        
    def executive_summary(self):
        """Generate executive summary with key business metrics"""
        lines = []
        lines.append("=" * 80)
        lines.append("MOROCCO AIRPORTS - EXECUTIVE SUMMARY")
        lines.append("=" * 80)
        
        total_flights = len(self.df)
        on_time_rate = (1 - self.df['is_delayed'].mean()) * 100
        avg_delay = self.df[self.df['is_delayed']]['delay_minutes'].mean()
        cancellation_rate = self.df['is_cancelled'].mean() * 100
        
        lines.append(f"📊 Total Flights Analyzed: {total_flights:,}")
        lines.append(f"⏰ On-Time Performance: {on_time_rate:.1f}%")
        lines.append(f"⏱️  Average Delay (when delayed): {avg_delay:.0f} minutes")
        lines.append(f"❌ Cancellation Rate: {cancellation_rate:.2f}%")
        
        # Airport performance
        airport_performance = self.df.groupby('data_airport').agg({
            'is_delayed': lambda x: (1 - x.mean()) * 100,
            'flight_id': 'count'
        }).round(1)
        airport_performance.columns = ['On_Time_Rate_%', 'Total_Flights']
        
        lines.append(f"\n🏆 Best Performing Airport: {airport_performance['On_Time_Rate_%'].idxmax()}")
        lines.append(f"    On-Time Rate: {airport_performance['On_Time_Rate_%'].max():.1f}%")
        
        lines.append(f"\n📈 Busiest Airport: {airport_performance['Total_Flights'].idxmax()}")
        lines.append(f"    Total Flights: {airport_performance['Total_Flights'].max():,}")
        
        # Top airlines
        top_airlines = self.df['airline'].value_counts().head(3)
        lines.append(f"\n✈️  Top Airlines by Flight Volume:")
        for i, (airline, count) in enumerate(top_airlines.items(), 1):
            lines.append(f"    {i}. {airline}: {count:,} flights")
        
        lines.append("\n" + "=" * 80)
        
        return lines
    
    def plot_airport_performance_dashboard(self):
        """Create comprehensive airport performance dashboard"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Airport Performance Dashboard - Morocco', fontsize=16, fontweight='bold', y=0.99)
        
        # 1. Flight volume by airport
        airport_volumes = self.df['data_airport'].value_counts()
        bars1 = ax1.bar(range(len(airport_volumes)), airport_volumes.values, 
                       color=colors['primary'], alpha=0.8)
        ax1.set_title('Flight Volume by Airport', fontweight='bold', pad=5)
        ax1.set_xlabel('Airport')
        ax1.set_ylabel('Number of Flights')
        ax1.set_xticks(range(len(airport_volumes)))
        ax1.set_xticklabels(airport_volumes.index, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom')
        
        # 2. On-time performance by airport
        otp_by_airport = self.df.groupby('data_airport')['is_delayed'].apply(lambda x: (1-x.mean())*100)
        bars2 = ax2.bar(range(len(otp_by_airport)), otp_by_airport.values, 
                       color=colors['success'], alpha=0.8)
        ax2.set_title('On-Time Performance by Airport', fontweight='bold', pad=5)
        ax2.set_xlabel('Airport')
        ax2.set_ylabel('On-Time Rate (%)')
        ax2.set_xticks(range(len(otp_by_airport)))
        ax2.set_xticklabels(otp_by_airport.index, rotation=45, ha='right')
        ax2.set_ylim(0, 100)
        
        # Add percentage labels
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # 3. Flight distribution by type
        flight_type_dist = self.df['flight_category'].value_counts()
        wedges, texts, autotexts = ax3.pie(flight_type_dist.values, 
                                          labels=flight_type_dist.index,
                                          autopct='%1.1f%%',
                                          colors=[colors['secondary'], colors['accent']],
                                          startangle=90)
        ax3.set_title('Domestic vs International Flights', fontweight='bold', pad=5)
        
        # 4. Average delay by airport (for delayed flights only)
        delayed_flights = self.df[self.df['is_delayed']]
        avg_delay_by_airport = delayed_flights.groupby('data_airport')['delay_minutes'].mean()
        bars4 = ax4.bar(range(len(avg_delay_by_airport)), avg_delay_by_airport.values, 
                       color=colors['warning'], alpha=0.8)
        ax4.set_title('Average Delay Duration by Airport', fontweight='bold', pad=5)
        ax4.set_xlabel('Airport')
        ax4.set_ylabel('Average Delay (minutes)')
        ax4.set_xticks(range(len(avg_delay_by_airport)))
        ax4.set_xticklabels(avg_delay_by_airport.index, rotation=45, ha='right')
        
        # Add minute labels
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}m', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('./outputs/02_airport_performance_dashboard.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    
    def plot_airline_analysis(self):
        """Comprehensive airline performance analysis"""
        # Get top 10 airlines by flight volume
        top_airlines = self.df['airline'].value_counts().head(10).index
        airline_data = self.df[self.df['airline'].isin(top_airlines)]
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Airline Performance Analysis - Top 10 Airlines', fontsize=16, fontweight='bold', y=0.99)
        
        # 1. Flight volume by airline
        airline_volumes = airline_data['airline'].value_counts()
        bars1 = ax1.barh(range(len(airline_volumes)), airline_volumes.values, 
                        color=colors['primary'], alpha=0.8)
        ax1.set_title('Flight Volume by Airline', fontweight='bold', pad=5)
        ax1.set_xlabel('Number of Flights')
        ax1.set_yticks(range(len(airline_volumes)))
        ax1.set_yticklabels(airline_volumes.index)
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{int(width):,}', ha='left', va='center', fontweight='bold')
        
        # 2. On-time performance by airline
        otp_by_airline = airline_data.groupby('airline')['is_delayed'].apply(lambda x: (1-x.mean())*100)
        otp_by_airline = otp_by_airline.sort_values(ascending=True)
        
        colors_otp = [colors['success'] if x >= 80 else colors['warning'] if x >= 70 else colors['danger'] 
                     for x in otp_by_airline.values]
        
        bars2 = ax2.barh(range(len(otp_by_airline)), otp_by_airline.values, 
                        color=colors_otp, alpha=0.8)
        ax2.set_title('On-Time Performance by Airline', fontweight='bold', pad=5)
        ax2.set_xlabel('On-Time Rate (%)')
        ax2.set_yticks(range(len(otp_by_airline)))
        ax2.set_yticklabels(otp_by_airline.index)
        ax2.set_xlim(0, 100)
        
        # Add percentage labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{width:.1f}%', ha='left', va='center', fontweight='bold')
        
        # 3. Aircraft model distribution
        top_aircraft = airline_data['aircraft_model'].value_counts().head(8)
        wedges, texts, autotexts = ax3.pie(top_aircraft.values, 
                                          labels=top_aircraft.index,
                                          autopct='%1.1f%%',
                                          colors=sns.color_palette("Set3", len(top_aircraft)),
                                          startangle=90)
        ax3.set_title('Aircraft Model Distribution', fontweight='bold', pad=5)
        
        # 4. Delay distribution
        delay_ranges = ['On Time', '15-30 min', '30-60 min', '60-120 min', '>120 min']
        delay_counts = [
            len(airline_data[airline_data['delay_minutes'] <= 15]),
            len(airline_data[(airline_data['delay_minutes'] > 15) & (airline_data['delay_minutes'] <= 30)]),
            len(airline_data[(airline_data['delay_minutes'] > 30) & (airline_data['delay_minutes'] <= 60)]),
            len(airline_data[(airline_data['delay_minutes'] > 60) & (airline_data['delay_minutes'] <= 120)]),
            len(airline_data[airline_data['delay_minutes'] > 120])
        ]
        
        bars4 = ax4.bar(delay_ranges, delay_counts, 
                       color=[colors['success'], colors['warning'], colors['warning'], 
                             colors['danger'], colors['danger']], alpha=0.8)
        ax4.set_title('Flight Delay Distribution', fontweight='bold', pad=5)
        ax4.set_xlabel('Delay Range')
        ax4.set_ylabel('Number of Flights')
        ax4.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('./outputs/03_airline_performance_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_route_analysis(self):
        """Analyze popular routes and destinations"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Route and Destination Analysis', fontsize=16, fontweight='bold', y=0.99)
        
        # 1. Top destinations from Morocco
        top_destinations = self.df['destination_city'].value_counts().head(10)
        bars1 = ax1.barh(range(len(top_destinations)), top_destinations.values, 
                        color=colors['secondary'], alpha=0.8)
        ax1.set_title('Top 10 Destinations from Morocco', fontweight='bold', pad=5)
        ax1.set_xlabel('Number of Flights')
        ax1.set_yticks(range(len(top_destinations)))
        ax1.set_yticklabels(top_destinations.index)
        
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{int(width):,}', ha='left', va='center', fontweight='bold')
        
        # 2. Top origin cities to Morocco
        top_origins = self.df['origin_city'].value_counts().head(10)
        bars2 = ax2.barh(range(len(top_origins)), top_origins.values, 
                        color=colors['accent'], alpha=0.8)
        ax2.set_title('Top 10 Origin Cities to Morocco', fontweight='bold', pad=5)
        ax2.set_xlabel('Number of Flights')
        ax2.set_yticks(range(len(top_origins)))
        ax2.set_yticklabels(top_origins.index)
        
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{int(width):,}', ha='left', va='center', fontweight='bold')
        
        # 3. International vs Domestic by Airport
        route_analysis = self.df.groupby(['data_airport', 'flight_category']).size().unstack(fill_value=0)
        route_analysis.plot(kind='bar', stacked=True, ax=ax3, 
                          color=[colors['primary'], colors['success']], alpha=0.8)
        ax3.set_title('Domestic vs International Flights by Airport', fontweight='bold', pad=5)
        ax3.set_xlabel('Airport')
        ax3.set_ylabel('Number of Flights')
        ax3.legend(title='Flight Type')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Top countries by flight volume
        top_countries = pd.concat([
            self.df['origin_country'].value_counts(),
            self.df['destination_country'].value_counts()
        ]).groupby(level=0).sum().sort_values(ascending=False).head(10)
        
        bars4 = ax4.bar(range(len(top_countries)), top_countries.values, 
                       color=colors['neutral'], alpha=0.8)
        ax4.set_title('Top 10 Countries by Flight Volume', fontweight='bold', pad=5)
        ax4.set_xlabel('Country')
        ax4.set_ylabel('Number of Flights')
        ax4.set_xticks(range(len(top_countries)))
        ax4.set_xticklabels(top_countries.index, rotation=45, ha='right')
        
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height):,}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('./outputs/04_route_destination_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_business_insights(self):
        """Generate actionable business insights"""
        lines = []
        lines.append("\n" + "=" * 80)
        lines.append("STRATEGIC BUSINESS INSIGHTS & RECOMMENDATIONS")
        lines.append("=" * 80)
        
        # Performance insights
        worst_performing_airport = self.df.groupby('data_airport')['is_delayed'].mean().idxmax()
        best_performing_airport = self.df.groupby('data_airport')['is_delayed'].mean().idxmin()
        
        lines.append("\n🎯 PERFORMANCE OPTIMIZATION OPPORTUNITIES:")
        lines.append(f"   • {worst_performing_airport} shows highest delay rates - investigate ground operations")
        lines.append(f"   • {best_performing_airport} demonstrates best practices - replicate across network")
        
        # Capacity insights
        busiest_hour = self.df['hour'].mode()[0]
        peak_day = self.df['day_of_week'].mode()[0]
        
        lines.append(f"\n📈 CAPACITY MANAGEMENT:")
        lines.append(f"   • Peak traffic hour: {busiest_hour}:00 - ensure adequate staffing")
        lines.append(f"   • Busiest day: {peak_day} - optimize resource allocation")
        
        # Revenue opportunities
        international_pct = (self.df['flight_category'] == 'International').mean() * 100
        lines.append(f"\n💰 REVENUE OPTIMIZATION:")
        lines.append(f"   • International flights: {international_pct:.1f}% of total volume")
        lines.append(f"   • Focus on premium international routes for higher margins")
        
        # Operational efficiency
        avg_terminal_utilization = self.df.groupby('terminal')['flight_id'].count().mean()
        lines.append(f"\n⚡ OPERATIONAL EFFICIENCY:")
        lines.append(f"   • Average terminal utilization: {avg_terminal_utilization:.0f} flights per terminal")
        lines.append(f"   • Consider load balancing across terminals during peak hours")
        
        # Customer experience
        severe_delay_pct = (self.df['delay_minutes'] > 60).mean() * 100
        lines.append(f"\n👥 CUSTOMER EXPERIENCE:")
        lines.append(f"   • Severe delays (>60min): {severe_delay_pct:.1f}% of flights")
        lines.append(f"   • Implement proactive passenger communication systems")
        
        lines.append("\n" + "=" * 80)
        
        return lines
    
    def save_summary_report(self):
        """Save complete text summary to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'./outputs/01_executive_summary_{timestamp}.txt'
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("🚀 MOROCCO AIRPORT ANALYSIS - BUSINESS INTELLIGENCE REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive summary
            executive_lines = self.executive_summary()
            for line in executive_lines:
                f.write(line + "\n")
            
            # Business insights
            insights_lines = self.generate_business_insights()
            for line in insights_lines:
                f.write(line + "\n")
            
            f.write(f"\n✅ Analysis Complete! All insights and visualizations saved to ./outputs/ folder.\n")
            f.write(f"Generated files:\n")
            f.write(f"  - 01_executive_summary_{timestamp}.txt (this file)\n")
            f.write(f"  - 02_airport_performance_dashboard.png\n")
            f.write(f"  - 03_airline_performance_analysis.png\n")
            f.write(f"  - 04_route_destination_analysis.png\n")
    
    def run_complete_analysis(self):
        """Execute the complete business analysis and save all outputs"""
        print("🚀 Starting Morocco Airport Analysis...")
        print("📁 Creating outputs in ./outputs/ folder...")
        
        print("📊 Generating Airport Performance Dashboard...")
        self.plot_airport_performance_dashboard()
        
        print("✈️  Evaluating Airline Performance...")
        self.plot_airline_analysis()
        
        print("🗺️  Examining Route Networks...")
        self.plot_route_analysis()
        
        print("📝 Generating Executive Summary Report...")
        self.save_summary_report()
        
        print("\n✅ Analysis Complete! All files saved to ./outputs/ folder:")

        return "Analysis completed successfully!"


def analyze(data_path):
    df = pd.read_csv(data_path)
    analyzer = MoroccoAirportAnalysis(df)
    analyzer.run_complete_analysis()

