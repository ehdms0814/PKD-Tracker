import pandas as pd
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.figure import Figure
from data_manager import DataManager

class Analyzer:

    def __init__(self, data_manager):
        self.data_manager = data_manager

    def get_dataframe(self):

        data = self.data_manager.load_all_data()
        if not data:
            return pd.DataFrame()

        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])

        numeric_cols = ['Sleep_Hours', 'Symptom_Count', 'Symptom_Score', 'Exercise_Duration', 'Medication_Count']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        if 'Exercise_Duration' in df.columns:
            df['Exercise_Hours'] = round(df['Exercise_Duration'] / 60.0, 2)

        return df

    def get_basic_stats(self):

        df = self.get_dataframe()
        if df.empty:
            return {"Error": "No data available."}

        stats = {
            "Total_Recorded_Days": len(df),
            "Average_Sleep_Hours": round(df['Sleep_Hours'].mean(), 1) if 'Sleep_Hours' in df.columns else 0,
            "Total_Symptom_Count": int(df['Symptom_Count'].sum()) if 'Symptom_Count' in df.columns else 0,
            "Average_Stability_Score": round(df['Symptom_Score'].mean(), 1) if 'Symptom_Score' in df.columns else 0,
        }
        return stats

    def get_correlations(self):

        df = self.get_dataframe()
        correlations = {}
        if df.empty or len(df) < 2:
            return correlations

        factors = ['Sleep_Hours', 'Medication_Count', 'Exercise_Hours']

        for col in factors:
            if col in df.columns and 'Symptom_Count' in df.columns:
                corr = df['Symptom_Count'].corr(df[col])
                correlations[f'Symptom_vs_{col}'] = round(corr, 2) if pd.notna(corr) else 0.0

        for col in factors:
            if col in df.columns and 'Symptom_Score' in df.columns:
                corr = df['Symptom_Score'].corr(df[col])
                correlations[f'Stability_vs_{col}'] = round(corr, 2) if pd.notna(corr) else 0.0

        return correlations

class Visualizer:

    def __init__(self, analyzer):
        self.analyzer = analyzer

    def create_symptoms_figure(self):

        df = self.analyzer.get_dataframe()

        fig = Figure(figsize=(7, 4.5)) 
        ax = fig.add_subplot(111)

        if df.empty or 'Symptom_Count' not in df.columns:
            ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', fontsize=12)
            ax.axis('off')
            return fig

        df_sorted = df.sort_values(by='Date')

        ax.plot(df_sorted['Date'], df_sorted['Symptom_Count'], marker='o', linestyle='-', label='Symptom Count', color='red')

        if 'Symptom_Score' in df_sorted.columns:
            ax.plot(df_sorted['Date'], df_sorted['Symptom_Score'], marker='s', linestyle='--', label='Stability Score', color='blue')

        if 'Sleep_Hours' in df_sorted.columns:
            ax.plot(df_sorted['Date'], df_sorted['Sleep_Hours'], marker='d', linestyle='-', label='Sleep Hours', color='purple')

        if 'Exercise_Hours' in df_sorted.columns:
            ax.plot(df_sorted['Date'], df_sorted['Exercise_Hours'], marker='*', linestyle=':', label='Exercise Hours', color='gold')

        if 'Medication_Count' in df_sorted.columns:
            ax.plot(df_sorted['Date'], df_sorted['Medication_Count'], marker='^', linestyle='-.', label='Medication Count', color='#2ca02c')

        ax.set_title('Daily Health Observations', fontsize=12)
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.grid(True, linestyle='--', alpha=0.6)

        ax.legend(fontsize=8, loc='center left', bbox_to_anchor=(1, 0.5))

        days_span = (df_sorted['Date'].max() - df_sorted['Date'].min()).days
        if pd.isna(days_span) or days_span <= 15:
            ax.xaxis.set_major_locator(mdates.DayLocator()) 
        else:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator()) 

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        fig.autofmt_xdate()

        fig.subplots_adjust(right=0.75) 
        return fig

    def create_transition_figure(self):

        df = self.analyzer.get_dataframe()

        fig = Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        if df.empty or 'Transition_Type' not in df.columns:
            ax.text(0.5, 0.5, "No Data Available", ha='center', va='center', fontsize=12)
            ax.axis('off')
            return fig

        counts = df['Transition_Type'].value_counts().reset_index()
        counts.columns = ['Transition_Type', 'Count']

        counts = counts[~counts['Transition_Type'].isin(['None', '', 'unknown'])]

        if counts.empty:
            ax.text(0.5, 0.5, "No Transition Data Recorded", ha='center', va='center', fontsize=12)
            ax.axis('off')
            return fig

        sns.barplot(data=counts, x='Transition_Type', y='Count', hue='Transition_Type', palette='viridis', legend=False, ax=ax)

        ax.set_title('Observations by Movement Transition Type', fontsize=12)
        ax.set_xlabel('Transition Context')
        ax.set_ylabel('Frequency')
        ax.tick_params(axis='x', rotation=30)

        fig.tight_layout()
        return fig
