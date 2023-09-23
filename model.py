from sqlalchemy import CHAR, Column, Date, DateTime, Integer, LargeBinary, Numeric, String, Table, Text, text
from sqlalchemy.ext.declarative import declarative_base
import torch
import torch.nn as nn

Base = declarative_base()
metadata = Base.metadata

class AisDataAbnrm(Base):
    __tablename__ = 'ais_data_air_abnrm'
    __table_args__ = {'comment': '일반대기 측정망 이상 자료'}
    
    msrmt_ymdh = Column(String(10), primary_key=True, nullable=False, comment='\t측정년월일시')
    msrstn_cd = Column(Numeric(6, 0), primary_key=True, nullable=False, comment='\t측정소코드')
    cntmn_dtl_cd = Column(Numeric(5, 0), primary_key=True, nullable=False, comment='\t오염물질상세코드')
    ft_cfmtn_flag = Column(String(2), comment='\t1차확정플래그')
    ft_cfmtn_dtl_cd = Column(String(4), comment='\t1차확정상세코드')
    ft_cfmtn_dnsty = Column(Numeric(24, 14), comment='\t1차확정농도')
    abnrm_data_cn = Column(String(4000), comment='\t비정상자료내용')
    abnrm_data_se_cd = Column(Numeric(2, 0), comment='\t비정상자료구분코드')
    abnrm_data_yn_cd = Column(Numeric(1, 0), comment='\t비정상자료여부코드')
    last_cfmtn_flag = Column(Numeric(2, 0), comment='\t최종확정FLAG')
    last_cfmtn_dtl_cd = Column(String(4), comment='\t최종확정상세코드')
    last_cfmtn_dnsty = Column(Numeric(24, 14), comment='\t최정확정농도')
    last_abnrm_data_cn = Column(String(50), comment='\t최종비정상자료내용')
    last_abnrm_data_rmk = Column(String(4), comment='\t최종비정상자료비고')
    last_cfmtn_yn_cd = Column(Numeric(1), comment='\t최정확정여부코드')
    last_abnrm_data_mdfcn_ymd = Column(String(8), comment='\t최종비정상자료수정일자')

class AisDataAir(Base):
    __tablename__ = 'ais_data_air'
    __table_args__ = {'comment': '일반대기 측정망 측정 자료'}


    data_knd_cd = Column(String(6), primary_key=True, nullable=False, comment='\t자료종류코드')
    msrstn_cd = Column(Numeric(6, 0), primary_key=True, nullable=False, comment='\t측정소코드')
    msrmt_ymdh = Column(String(10), primary_key=True, nullable=False, comment='\t측정년월일시')
    so2_dtl_flag = Column(Numeric(1, 0), comment='\t아황산가스상세플래그')
    so2_dtl_cd = Column(String(4), comment='\t아황산가스상세코드')
    so2_dnsty = Column(Numeric(24, 14), comment='\t아황산가스농도')
    pm_dtl_flag = Column(Numeric(1, 0), comment='\t미세먼지상세플래그')
    pm_dtl_cd = Column(String(4), comment='\t미세먼지상세코드')
    pm_dnsty = Column(Numeric(24, 14), comment='미세먼지농도')
    oz_dtl_flag = Column(Numeric(1, 0), comment='오존상세플래그')
    oz_dtl_cd = Column(String(4), comment='오존상세코드')
    oz_dnsty = Column(Numeric(24, 14), comment='오존농도')
    no2_dtl_flag = Column(Numeric(1, 0), comment='이산화질소상세플래그')
    no2_dtl_cd = Column(String(4), comment='이산화질소상세코드')
    no2_dnsty = Column(Numeric(24, 14), comment='이산화질소농도')
    co_dtl_flag = Column(Numeric(1, 0), comment='일산화탄소상세플래그')
    co_dtl_cd = Column(String(4), comment='일산화탄소상세코드')
    co_dnsty = Column(Numeric(24, 14), comment='일산화탄소농도')
    thc_dtl_flag = Column(Numeric(1, 0), comment='총탄화수소상세플래그')
    thc_dtl_cd = Column(String(4), comment='총탄화수소상세코드')
    thc_dnsty = Column(Numeric(24, 14), comment='총탄화수소농도')
    nox_dtl_flag = Column(Numeric(1, 0), comment='질소산화물상세플래그')
    nox_dtl_cd = Column(String(4), comment='질소산화물상세코드')
    nox_dnsty = Column(Numeric(24, 14), comment='질소산화물농도')
    nmo_dtl_flag = Column(Numeric(1, 0), comment='일산화질소상세플래그')
    nmo_dtl_cd = Column(String(4), comment='일산화질소상세코드')
    nmo_dnsty = Column(Numeric(24, 14), comment='일산화질소농도')
    nmhc_dtl_flag = Column(Numeric(1, 0), comment='비메탄계탄화수소상세플래그')
    nmhc_dtl_cd = Column(String(4), comment='비메탄계탄화수소상세코드')
    nmhc_dnsty = Column(Numeric(24, 14), comment='비메탄계탄화수소농도')
    ch4_dtl_flag = Column(Numeric(1, 0), comment='메테인상세플래그')
    ch4_dtl_cd = Column(String(4), comment='메테인상세코드')
    ch4_dnsty = Column(Numeric(24, 14), comment='메테인농도')
    wd_dtl_flag = Column(Numeric(1, 0), comment='풍향상세플래그')
    wd_dtl_cd = Column(String(4), comment='풍향상세코드')
    wd = Column(Numeric(4, 0), comment='풍향')
    ws_dtl_flag = Column(Numeric(1, 0), comment='풍속상세플래그')
    ws_dtl_cd = Column(String(4), comment='풍속상세코드')
    ws = Column(Numeric(10, 4), comment='풍속')
    ta_dtl_flag = Column(Numeric(1, 0), comment='기온상세플래그')
    ta_dtl_cd = Column(String(4), comment='기온상세코드')
    ta = Column(Numeric(10, 5), comment='기온')
    pm25_dtl_flag = Column(Numeric(1, 0), comment='초미세먼지상세플래그')
    pm25_dtl_cd = Column(String(4), comment='초미세먼지상세코드')
    pm25_dnsty = Column(Numeric(24, 14), comment='초미세먼지농도')
    vs_dist_dtl_flag = Column(Numeric(1, 0), comment='시정거리상세플래그')
    vs_dist_dtl_cd = Column(String(4), comment='시정거리상세코드')
    vs_dist = Column(Numeric(10, 3), comment='시정거리')
    siamt_dtl_flag = Column(Numeric(1, 0), comment='일사량상세플래그')
    siamt_dtl_cd = Column(String(4), comment='일사량상세코드')
    siamt = Column(Numeric(10, 5), comment='일사량')
    hd_dtl_flag = Column(Numeric(1, 0), comment='습도상세플래그')
    hd_dtl_cd = Column(String(4), comment='습도상세코드')
    hd = Column(Numeric(10, 4), comment='습도')
    tmpr1_dtl_flag = Column(Numeric(1, 0), comment='임시1상세플래그')
    tmpr1_dtl_cd = Column(String(4), comment='임시1상세코드')
    tmpr1_dnsty = Column(Numeric(24, 14), comment='임시1농도')
    tmpr2_dtl_flag = Column(Numeric(1, 0), comment='임시2상세플래그')
    tmpr2_dtl_cd = Column(String(4), comment='임시2상세코드')
    tmpr2_dnsty = Column(Numeric(24, 14), comment='임시2농도')
    tmpr3_dtl_flag = Column(Numeric(1, 0), comment='임시3상세플래그')
    tmpr3_dtl_cd = Column(String(4), comment='임시3상세코드')
    tmpr3_dnsty = Column(Numeric(24, 14), comment='임시3농도')
    tmpr4_dtl_flag = Column(Numeric(1, 0), comment='임시4상세플래그')
    tmpr4_dtl_cd = Column(String(4), comment='임시4상세코드')
    tmpr4_dnsty = Column(Numeric(24, 14), comment='임시4농도')
    tmpr5_dtl_flag = Column(Numeric(1, 0), comment='임시5상세플래그')
    tmpr5_dtl_cd = Column(String(4), comment='임시5상세코드')
    tmpr5_dnsty = Column(Numeric(24, 14), comment='임시5농도')
    tmpr6_dtl_flag = Column(Numeric(1, 0), comment='임시6상세플래그')
    tmpr6_dtl_cd = Column(String(4), comment='임시6상세코드')
    tmpr6_dnsty = Column(Numeric(24, 14), comment='임시6농도')

class CBR_1D(nn.Module):
    def __init__(self,in_channels,out_channels,kernel=9,stride=1,padding=4):
        super().__init__()
        self.seq_list = [
        nn.Conv1d(in_channels,out_channels,kernel,stride,padding,bias=False),
        nn.BatchNorm1d(out_channels),
        nn.ReLU()]
        
        self.seq = nn.Sequential(*self.seq_list)
        
    def forward(self,x):
        return self.seq(x)

class Unet_1D(nn.Module):
    def __init__(self,class_n,layer_n):
        super().__init__()
        
        ### ------- encoder -----------
        self.enc1_1 = CBR_1D(1,layer_n)
        self.enc1_2 = CBR_1D(layer_n,layer_n)
        self.enc1_3 = CBR_1D(layer_n,layer_n)
        
        self.enc2_1 = CBR_1D(layer_n,layer_n*2)
        self.enc2_2 = CBR_1D(layer_n*2,layer_n*2)
        
        self.enc3_1 = CBR_1D(layer_n*2,layer_n*4)
        self.enc3_2 = CBR_1D(layer_n*4,layer_n*4)
        
        self.enc4_1 = CBR_1D(layer_n*4,layer_n*8)
        self.enc4_2 = CBR_1D(layer_n*8,layer_n*8)
    
        ### ------- decoder -----------
        self.upsample_3 = nn.ConvTranspose1d(layer_n*8,layer_n*8,kernel_size=8,stride=2,padding=3)
        self.dec3_1 = CBR_1D(layer_n*4+layer_n*8,layer_n*4)
        self.dec3_2 = CBR_1D(layer_n*4,layer_n*4)
        
        self.upsample_2 = nn.ConvTranspose1d(layer_n*4,layer_n*4,kernel_size=8,stride=2,padding=3)
        self.dec2_1 = CBR_1D(layer_n*2+layer_n*4,layer_n*2)
        self.dec2_2 = CBR_1D(layer_n*2,layer_n*2)
        
        self.upsample_1 = nn.ConvTranspose1d(layer_n*2,layer_n*2,kernel_size=8,stride=2,padding=3)
        self.dec1_1 = CBR_1D(layer_n*1+layer_n*2,layer_n*1)
        self.dec1_2 = CBR_1D(layer_n*1,layer_n*1)
        self.dec1_3 = CBR_1D(layer_n*1,class_n)
        self.dec1_4 = CBR_1D(class_n,class_n)
    
    def forward(self,x):
        enc1 = self.enc1_1(x)
        enc1 = self.enc1_2(enc1)
        enc1 = self.enc1_3(enc1)
        
        enc2 = nn.functional.max_pool1d(enc1,2)
        enc2 = self.enc2_1(enc2)
        enc2 = self.enc2_2(enc2)
        
        enc3 = nn.functional.max_pool1d(enc2,2)
        enc3 = self.enc3_1(enc3)
        enc3 = self.enc3_2(enc3)
        
        enc4 = nn.functional.max_pool1d(enc3,2)        
        enc4 = self.enc4_1(enc4)
        enc4 = self.enc4_2(enc4)
        
        dec3 = self.upsample_3(enc4)
        dec3 = self.dec3_1(torch.cat([enc3,dec3],dim=1))
        dec3 = self.dec3_2(dec3)
        
        dec2 = self.upsample_2(dec3)
        dec2 = self.dec2_1(torch.cat([enc2,dec2],dim=1))
        dec2 = self.dec2_2(dec2)
        
        dec1 = self.upsample_1(dec2)
        dec1 = self.dec1_1(torch.cat([enc1,dec1],dim=1))
        dec1 = self.dec1_2(dec1)
        dec1 = self.dec1_3(dec1)
        out = self.dec1_4(dec1)
        
        return out