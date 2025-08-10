#!/usr/bin/env python3
"""
GliomaScope Dual Interface Demonstration

This script demonstrates how both the terminal and web interfaces can work together.
It shows that they use the same underlying data and analysis modules.
"""

import os
import sys
import time
import webbrowser
from threading import Thread

def run_web_interface():
    """Run the web interface in a separate thread"""
    print("🌐 Starting Web Interface...")
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5001, use_reloader=False)
    except Exception as e:
        print(f"❌ Web interface error: {e}")

def demonstrate_terminal_functions():
    """Demonstrate some terminal functions"""
    print("\n" + "="*60)
    print("🖥️  TERMINAL INTERFACE DEMONSTRATION")
    print("="*60)
    
    try:
        # Import terminal modules
        from src.data_handling.Data_loader import DataManager
        from src.utils.Utils import list_available_genes
        
        # Create data manager instance
        data_manager = DataManager()
        
        print("✅ Terminal modules imported successfully")
        print("✅ DataManager initialized")
        
        # Check for existing data
        if os.path.exists('cleaned_data/metadata_cleaned.csv'):
            print("📊 Found existing metadata file")
            data_manager.load_file_smart('cleaned_data/metadata_cleaned.csv')
            print(f"   - Loaded {data_manager.metadata.shape[0]} samples")
            print(f"   - Metadata columns: {len(data_manager.metadata.columns)}")
        
        if os.path.exists('cleaned_data/expression_cleaned.csv'):
            print("🧬 Found existing expression file")
            data_manager.load_expression('cleaned_data/expression_cleaned.csv')
            print(f"   - Loaded {data_manager.expression.shape[0]} samples")
            print(f"   - Expression features: {data_manager.expression.shape[1]-1}")
        
        if data_manager.metadata is None and data_manager.expression is None:
            print("📝 No existing data found")
            print("   Use either interface to load data first")
        
        print("\n✅ Terminal interface is fully functional")
        
    except Exception as e:
        print(f"❌ Terminal interface error: {e}")

def main():
    """Main demonstration function"""
    print("\n" + "="*70)
    print("🧬 GliomaScope Dual Interface Demonstration 🧬")
    print("="*70)
    print("This demo shows both interfaces working together:")
    print("• Web Interface  → Modern GUI with DNA matrix theme")
    print("• Terminal Interface → Command-line version with same functions")
    print("• Shared Data → Both use the same underlying data and modules")
    print("="*70)
    
    # Start web interface in background
    web_thread = Thread(target=run_web_interface, daemon=True)
    web_thread.start()
    
    # Give web interface time to start
    time.sleep(2)
    
    # Open web browser
    print("🚀 Opening web interface in browser...")
    try:
        webbrowser.open('http://localhost:5001')
        print("✅ Web interface should open in your browser")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print("   Please open http://localhost:5001 manually")
    
    # Demonstrate terminal functions
    demonstrate_terminal_functions()
    
    print("\n" + "="*60)
    print("🎯 DUAL INTERFACE FEATURES")
    print("="*60)
    print("1. 🌐 Web Interface (http://localhost:5001)")
    print("   • Modern GUI with biotech DNA matrix theme")
    print("   • All 13 functions with interactive forms")
    print("   • Real-time visualization with Plotly")
    print("   • Responsive design for all devices")
    print("")
    print("2. 🖥️  Terminal Interface (python Main.py)")
    print("   • Command-line version with same 13 functions")
    print("   • Advanced scripting capabilities")
    print("   • Detailed console output")
    print("   • Batch processing friendly")
    print("")
    print("3. 🔄 Shared Features")
    print("   • Same underlying Python modules")
    print("   • Compatible data formats")
    print("   • Identical analysis results")
    print("   • Can run simultaneously")
    
    print("\n" + "="*60)
    print("📋 NEXT STEPS")
    print("="*60)
    print("1. Use the web interface to upload/analyze data")
    print("2. Try the terminal version: python3 Main.py")
    print("3. Notice how both interfaces share the same data")
    print("4. Use whichever interface suits your workflow!")
    print("")
    print("Press Ctrl+C to stop the web server...")
    print("="*60)
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped. Thank you for trying GliomaScope!")
        print("   Both interfaces are available anytime you need them.")

if __name__ == '__main__':
    main()