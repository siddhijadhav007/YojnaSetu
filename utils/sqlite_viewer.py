import sqlite3
import pandas as pd
from tabulate import tabulate

def view_schemes(db_file="yojna_setu_ai_schemes.db"):
    """
    Interactive SQLite database viewer for schemes
    """
    conn = sqlite3.connect(db_file)

    print("🎯 Yojna Setu.ai Schemes Database Viewer")
    print("=" * 50)

    while True:
        print("\n📋 Available Commands:")
        print("1. View all schemes (first 10)")
        print("2. Search by category")
        print("3. Search by state/type")
        print("4. Search by income range")
        print("5. Search by age range")
        print("6. View scheme details by ID")
        print("7. Show database statistics")
        print("8. Export to CSV")
        print("9. Exit")

        try:
            choice = input("\nEnter your choice (1-9): ").strip()

            if choice == "1":
                df = pd.read_sql_query("SELECT scheme_id, scheme_name, category, benefit_amount FROM schemes LIMIT 10", conn)
                print("\n📊 First 10 Schemes:")
                print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

            elif choice == "2":
                # Show available categories
                categories = pd.read_sql_query("SELECT DISTINCT category FROM schemes ORDER BY category", conn)
                print("\n📂 Available Categories:")
                for i, cat in enumerate(categories['category'], 1):
                    print(f"{i}. {cat}")

                cat_choice = input("\nEnter category name: ").strip()
                if cat_choice:
                    query = f"SELECT scheme_id, scheme_name, benefit_amount, min_age, max_age FROM schemes WHERE category LIKE '%{cat_choice}%' LIMIT 10"
                    df = pd.read_sql_query(query, conn)
                    print(f"\n📊 Schemes in '{cat_choice}':")
                    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

            elif choice == "3":
                # Show available scheme types
                types = pd.read_sql_query("SELECT DISTINCT scheme_type FROM schemes ORDER BY scheme_type", conn)
                print("\n🏛️ Available Scheme Types:")
                for i, typ in enumerate(types['scheme_type'], 1):
                    print(f"{i}. {typ}")

                type_choice = input("\nEnter scheme type: ").strip()
                if type_choice:
                    query = f"SELECT scheme_id, scheme_name, category, benefit_amount FROM schemes WHERE scheme_type LIKE '%{type_choice}%' LIMIT 10"
                    df = pd.read_sql_query(query, conn)
                    print(f"\n📊 {type_choice} Schemes:")
                    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

            elif choice == "4":
                min_inc = input("Enter minimum income (₹): ").strip()
                max_inc = input("Enter maximum income (₹): ").strip()

                if min_inc and max_inc:
                    query = f"""
                    SELECT scheme_id, scheme_name, category, benefit_amount, min_income, max_income
                    FROM schemes
                    WHERE (min_income <= {max_inc} OR min_income IS NULL)
                    AND (max_income >= {min_inc} OR max_income IS NULL)
                    LIMIT 10
                    """
                    df = pd.read_sql_query(query, conn)
                    print(f"\n📊 Schemes for income range ₹{min_inc} - ₹{max_inc}:")
                    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

            elif choice == "5":
                min_age = input("Enter minimum age: ").strip()
                max_age = input("Enter maximum age: ").strip()

                if min_age and max_age:
                    query = f"""
                    SELECT scheme_id, scheme_name, category, benefit_amount, min_age, max_age
                    FROM schemes
                    WHERE (min_age <= {max_age} OR min_age IS NULL)
                    AND (max_age >= {min_age} OR max_age IS NULL)
                    LIMIT 10
                    """
                    df = pd.read_sql_query(query, conn)
                    print(f"\n📊 Schemes for age range {min_age} - {max_age}:")
                    print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

            elif choice == "6":
                scheme_id = input("Enter scheme ID: ").strip()
                if scheme_id:
                    query = f"SELECT * FROM schemes WHERE scheme_id = {scheme_id}"
                    df = pd.read_sql_query(query, conn)
                    if not df.empty:
                        print(f"\n📋 Details for Scheme ID {scheme_id}:")
                        for col in df.columns:
                            value = df[col].iloc[0]
                            if pd.notna(value):
                                print(f"{col}: {value}")
                    else:
                        print("❌ Scheme not found!")

            elif choice == "7":
                # Database statistics
                stats = {}

                # Total schemes
                total = pd.read_sql_query("SELECT COUNT(*) as count FROM schemes", conn)['count'].iloc[0]
                stats['Total Schemes'] = total

                # Categories count
                categories = pd.read_sql_query("SELECT category, COUNT(*) as count FROM schemes GROUP BY category ORDER BY count DESC", conn)
                print("\n📊 Database Statistics:")
                print(f"Total Schemes: {total}")
                print("\n📂 Schemes by Category:")
                print(tabulate(categories, headers=['Category', 'Count'], tablefmt='grid', showindex=False))

                # Scheme types
                types = pd.read_sql_query("SELECT scheme_type, COUNT(*) as count FROM schemes GROUP BY scheme_type ORDER BY count DESC", conn)
                print("\n🏛️ Schemes by Type:")
                print(tabulate(types, headers=['Type', 'Count'], tablefmt='grid', showindex=False))

            elif choice == "8":
                filename = input("Enter CSV filename (without .csv): ").strip()
                if filename:
                    df = pd.read_sql_query("SELECT * FROM schemes", conn)
                    df.to_csv(f"{filename}.csv", index=False)
                    print(f"✅ Exported to {filename}.csv")

            elif choice == "9":
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice! Please enter 1-9.")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    conn.close()

if __name__ == "__main__":
    view_schemes()