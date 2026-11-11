import os, requests, streamlit as st
API=os.getenv("API_URL","http://localhost:8000")
st.set_page_config(page_title="DormMate",page_icon="🏠",layout="wide")
st.title("🏠 DormMate")
st.caption("Жатақханадағы бөлмелер мен студент өтініштерін басқару")
def get(path,params=None):
    r=requests.get(API+path,params=params,timeout=5); r.raise_for_status(); return r.json()
def post(path,data):return requests.post(API+path,json=data,timeout=5)
def patch(path,data):return requests.patch(API+path,json=data,timeout=5)
def delete(path):return requests.delete(API+path,timeout=5)
def as_table(rows, labels): return [{labels.get(k, k): v for k, v in row.items()} for row in rows]
try: rooms=get("/rooms"); students=get("/students"); apps=get("/applications")
except requests.RequestException as e: st.error(f"API серверіне қосылу мүмкін болмады: {e}"); st.stop()
a,b,c=st.columns(3); a.metric("Бөлме саны",len(rooms)); b.metric("Студент саны",len(students)); c.metric("Қаралудағы өтініш",sum(x["status"]=="Қаралуда" for x in apps))
t1,t2,t3=st.tabs(["Бөлмелер","Студенттер","Өтініштер"])
with t1:
    building=st.text_input("Корпус бойынша сүзгі",key="building")
    minf,maxf=st.columns(2); low=minf.number_input("Ең төмен ақы",min_value=0.0,value=0.0); high=maxf.number_input("Ең жоғары ақы",min_value=0.0,value=100000.0)
    data=get("/rooms",{"building":building or None,"min_fee":low,"max_fee":high}); st.dataframe(as_table(data,{"id":"Бөлме ID","building":"Корпус","room_number":"Бөлме №","capacity":"Сыйымдылығы","occupied_places":"Тұрғын саны","available_places":"Бос орын","monthly_fee":"Айлық төлем (₸)"}),use_container_width=True,hide_index=True)
    with st.expander("Бөлме қосу"):
        with st.form("room"):
            bld=st.text_input("Корпус"); num=st.text_input("Бөлме нөмірі"); cap=st.number_input("Сыйымдылығы",min_value=1,max_value=12,value=2); fee=st.number_input("Айлық төлем",min_value=0.0)
            if st.form_submit_button("Қосу"):
                r=post("/rooms",{"building":bld,"room_number":num,"capacity":cap,"monthly_fee":fee}); st.success("Қосылды") if r.ok else st.error(r.text); st.rerun() if r.ok else None
    if data:
        rid=st.selectbox("Өңдеу/жою бөлмесі",data,format_func=lambda x:f"{x['building']} · {x['room_number']} · бос орын: {x.get('available_places',x['capacity'])}")
        with st.form("room_update"):
            fee2=st.number_input("Жаңа айлық төлем",min_value=0.0,value=float(rid["monthly_fee"]))
            if st.form_submit_button("Төлемді өзгерту"):
                r=patch(f"/rooms/{rid['id']}",{"monthly_fee":fee2}); st.success("Жаңартылды") if r.ok else st.error(r.text); st.rerun() if r.ok else None
        if st.button("Таңдалған бөлмені жою",key="delete_room"):
            r=delete(f"/rooms/{rid['id']}"); st.success("Жойылды") if r.ok else st.error(r.text); st.rerun() if r.ok else None
with t2:
    query=st.text_input("Аты бойынша іздеу"); data=get("/students",{"search":query or None}); st.dataframe(as_table(data,{"id":"Студент ID","full_name":"Аты-жөні","student_number":"Студенттік билет №","faculty":"Факультет","phone":"Телефон"}),use_container_width=True,hide_index=True)
    with st.expander("Студент қосу"):
        with st.form("student"):
            name=st.text_input("Аты-жөні"); sn=st.text_input("Студент нөмірі"); fac=st.text_input("Факультет"); phone=st.text_input("Телефон (үлгі)",placeholder="+7 (7XX) XXX-XX-XX")
            if st.form_submit_button("Тіркеу"):
                r=post("/students",{"full_name":name,"student_number":sn,"faculty":fac,"phone":phone}); st.success("Тіркелді") if r.ok else st.error(r.text); st.rerun() if r.ok else None
    if data:
        chosen=st.selectbox("Өңделетін студент",data,format_func=lambda x:f"{x['full_name']} · {x['student_number']}")
        with st.expander("Студент мәліметін өзгерту"):
            with st.form("student_update"):
                name2=st.text_input("Аты-жөні",value=chosen["full_name"])
                faculty2=st.text_input("Факультет",value=chosen["faculty"])
                phone2=st.text_input("Телефон",value=chosen["phone"])
                if st.form_submit_button("Өзгерістерді сақтау"):
                    r=patch(f"/students/{chosen['id']}",{"full_name":name2,"faculty":faculty2,"phone":phone2})
                    if r.ok:
                        st.success("Студент жаңартылды")
                        st.rerun()
                    else:
                        st.error(r.text)
        if st.button("Таңдалған студентті жою",key="student_delete"):
            r=delete(f"/students/{chosen['id']}")
            if r.ok:
                st.success("Студент жойылды")
                st.rerun()
            else:
                st.error(r.text)
with t3:
    status=st.selectbox("Өтініш мәртебесі",["Барлығы","Қаралуда","Қабылданды","Қабылданбады"]); data=get("/applications",{"status":status if status!="Барлығы" else None}); st.dataframe(as_table(data,{"id":"Өтініш №","student_id":"Студент ID","room_id":"Бөлме ID","submitted_at":"Өтініш күні","status":"Мәртебесі","comment":"Түсініктеме"}),use_container_width=True,hide_index=True)
    if students and rooms:
        with st.expander("Өтініш қосу"):
            with st.form("application"):
                stu=st.selectbox("Студент",students,format_func=lambda x:f"{x['full_name']} ({x['student_number']})"); room=st.selectbox("Қалаған бөлме",rooms,format_func=lambda x:f"{x['building']} · {x['room_number']} · бос орын: {x.get('available_places',x['capacity'])}"); comment=st.text_input("Түсініктеме")
                if st.form_submit_button("Өтініш жіберу"):
                    r=post("/applications",{"student_id":stu["id"],"room_id":room["id"],"comment":comment or None}); st.success("Жіберілді") if r.ok else st.error(r.text); st.rerun() if r.ok else None
    if data:
        item=st.selectbox("Өңдеу/жою өтініші",data,format_func=lambda x:f"№{x['id']} · {x['status']}")
        with st.form("app_update"):
            state=st.selectbox("Жаңа мәртебе",["Қаралуда","Қабылданды","Қабылданбады"]); note=st.text_input("Түсініктеме",value=item.get("comment") or "")
            if st.form_submit_button("Мәртебені жаңарту"):
                r=patch(f"/applications/{item['id']}",{"status":state,"comment":note or None}); st.success("Жаңартылды") if r.ok else st.error(r.text); st.rerun() if r.ok else None
        if st.button("Өтінішті жою"):
            r=delete(f"/applications/{item['id']}"); st.success("Жойылды") if r.ok else st.error(r.text); st.rerun() if r.ok else None
