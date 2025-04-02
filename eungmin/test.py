import pyvista as pv
import streamlit as st
from stpyvista import stpyvista

# 스트림릿 앱 제목 설정
st.title("3D 자동차 시각화")

# PyVista plotter 객체 생성
plotter = pv.Plotter(window_size=[400, 400])

# 자동차 모양의 3D 모델 생성 (예: cube로 대체)
mesh = pv.Cube(center=(0, 0, 0))

# 모델에 스칼라 필드 추가
mesh['myscalar'] = mesh.points[:, 2] * mesh.points[:, 0]

# 모델을 plotter에 추가
plotter.add_mesh(mesh, scalars='myscalar', cmap='bwr')

# 배경색 설정
plotter.background_color = 'white'

# isometric 뷰로 설정
plotter.view_isometric()

# 스트림릿에 3D 시각화 표시
stpyvista(plotter, key="car_model")
