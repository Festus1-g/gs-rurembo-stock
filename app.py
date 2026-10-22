with tab_p2:
        st.subheader("Tunganya no Kubika Umushahara n'Imisanzu ya RSSB (Pension, CBHI, Maternity)")
        conn = sqlite3.connect(DB_FILE)
        df_emp = pd.read_sql_query("SELECT * FROM employees", conn)
        conn.close()
        
        if df_emp.empty:
            st.warning("Banza wandike abakozi muri 'Abakozi n'Amasezerano' kugira ngo ubone uko ubahemba.")
        else:
            selected_emp = st.selectbox("Hitamo Umukozi", df_emp['full_name'].tolist())
            emp_row = df_emp[df_emp['full_name'] == selected_emp].iloc[0]
            default_salary = float(emp_row['basic_salary']) if 'basic_salary' in emp_row else 0.0
            
            c1, c2 = st.columns(2)
            with c1:
                month_year = st.text_input("Ukwezi n'Umwaka (Urugero: October 2026)")
                basic_salary = st.number_input("Umushahara w'Ibanze (Basic Salary Frw)", value=default_salary, step=1000.0)
                allowances = st.number_input("Inyongera / Agahimbazamusyi (Allowances Frw)", min_value=0.0, step=500.0)
                
            with c2:
                # 1. Pansion (6% cyangwa nk'uko bisabwa)
                auto_pension = basic_salary * 0.06
                pension_deduction = st.number_input("Pansion (RSSB Pension 6%)", value=float(auto_pension), step=100.0)
                
                # 2. CBHI (Community Based Health Insurance / Mituweli cyangwa ubwishingizi)
                cbhi_deduction = st.number_input("CBHI / Ubwishingizi bw'Indwara (Frw)", value=0.0, step=100.0)
                
                # 3. Maternity Leave (Umusanzu w'Uruhinja/Ubwiteganyirize bw'Urupfu n'Uburumbuke)
                auto_maternity = basic_salary * 0.003 # 0.3% cyangwa se ushobora kuyihindura
                maternity_deduction = st.number_input("Maternity Leave Contribution (Frw)", value=float(auto_maternity), step=50.0)
                
                other_loans = st.number_input("Ibindi bikatwa (Loans / Advance Frw)", min_value=0.0, step=500.0)
                payment_date = st.date_input("Itariki yo Kwishyura")
                
                # Igiteranyo cy'ukatwa cyose (Total Deductions)
                total_deductions = pension_deduction + cbhi_deduction + maternity_deduction + other_loans
                net_salary = (basic_salary + allowances) - total_deductions
                
                st.info(f"**Igiteranyo cy'Ibyakatwe (Total Deductions):** {total_deductions:,.2f} Frw")
                st.info(f"**Umushahara w'Umusaruro (Net Salary):** {net_salary:,.2f} Frw")
                
            if st.button("💾 Bika Umushahara n'Imisanzu ya RSSB"):
                if month_year:
                    try:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute('''
                            INSERT INTO payroll (month_year, full_name, basic_salary, allowances, deductions, net_salary, payment_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (month_year, selected_emp, basic_salary, allowances, total_deductions, net_salary, payment_date.strftime("%Y-%m-%d")))
                        conn.commit()
                        conn.close()
                        st.success(f"Umushahara wa **{selected_emp}** w'ukwezi kwa **{month_year}** hamwe na RSSB wabikiwe neza!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Harimo ikosa: {e}")
                else:
                    st.warning("Andika ukwezi n'umwaka!")
