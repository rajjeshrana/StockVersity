"""Compact, desktop-first StockVersity dashboard."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class CompactDashboard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
        QWidget { background:#080f1c; color:#e9eef8; font-family:'Segoe UI'; }
        QFrame#card { background:#0d1727; border:1px solid #23344e; border-radius:8px; }
        QLabel.title { font-size:14px; font-weight:700; } QLabel.muted { color:#97a8c0; font-size:11px; }
        QLabel.value { font-size:22px; font-weight:700; } QLabel.green { color:#38df88; } QLabel.red { color:#ff5867; }
        """)
        root=QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(14)
        top=QGridLayout(); top.setHorizontalSpacing(12)
        for i,(name,value,change,up) in enumerate((('NIFTY 50','25,488.90','+243.60 (+0.97%)',1),('BANK NIFTY','57,920.15','+512.45 (+0.89%)',1),('SENSEX','83,502.35','+775.30 (+0.94%)',1),('INDIA VIX','12.42','-0.35 (-2.74%)',0))): top.addWidget(self.index_card(name,value,change,up),0,i)
        top.addWidget(self.breadth(),0,4); top.setColumnStretch(4,2); root.addLayout(top)
        middle=QGridLayout(); middle.setHorizontalSpacing(12)
        middle.addWidget(self.opportunities(),0,0); middle.addWidget(self.sectors(),0,1); middle.addWidget(self.heatmap(),0,2)
        middle.setColumnStretch(0,4); middle.setColumnStretch(1,3); middle.setColumnStretch(2,3); root.addLayout(middle,3)
        bottom=QGridLayout(); bottom.setHorizontalSpacing(12)
        bottom.addWidget(self.summary(),0,0); bottom.addWidget(self.movers(),0,1); bottom.addWidget(self.alerts(),0,2); bottom.addWidget(self.news(),0,3)
        for i in range(4): bottom.setColumnStretch(i,1)
        root.addLayout(bottom,2)

    def card(self):
        w=QFrame(); w.setObjectName('card'); return w
    def index_card(self,n,v,c,up):
        w=self.card(); l=QVBoxLayout(w); l.setContentsMargins(16,13,16,13); l.addWidget(QLabel(n,objectName='title')); l.addWidget(QLabel(v,objectName='value')); x=QLabel(c); x.setObjectName('green' if up else 'red'); l.addWidget(x); spark=QLabel('╱╲╱╲╱╲╱╲╱╲'); spark.setObjectName('green' if up else 'red'); spark.setAlignment(Qt.AlignRight); l.addWidget(spark); return w
    def breadth(self):
        w=self.card(); l=QVBoxLayout(w); l.setContentsMargins(16,13,16,13); l.addWidget(QLabel('MARKET BREADTH',objectName='title')); row=QHBoxLayout(); a=QLabel('1452\nADVANCES'); a.setObjectName('green'); a.setAlignment(Qt.AlignCenter); g=QLabel('◜ 112 ◝\nUNCHANGED'); g.setAlignment(Qt.AlignCenter); d=QLabel('256\nDECLINES'); d.setObjectName('red'); d.setAlignment(Qt.AlignCenter); row.addWidget(a); row.addWidget(g); row.addWidget(d); l.addLayout(row); return w
    def opportunities(self):
        w=self.card(); l=QVBoxLayout(w); l.setContentsMargins(16,12,16,10); l.addWidget(QLabel('TOP OPPORTUNITIES',objectName='title')); l.addWidget(QLabel('Best-ranked market setups',objectName='muted'))
        for i,(s,p,score,rr) in enumerate((('HAL','VCP',97,'1:4.2'),('BEL','ORB',95,'1:3.6'),('ABB','FLAG',93,'1:3.1'),('TATAMOTORS','BREAKOUT',90,'1:2.8'),('ICICIBANK','VCP',89,'1:3.4')),1):
            r=QHBoxLayout(); r.addWidget(QLabel(str(i))); r.addWidget(QLabel(s)); tag=QLabel(p); tag.setStyleSheet('background:#382a63;padding:4px;border-radius:4px;'); r.addWidget(tag); scorel=QLabel(str(score)); scorel.setObjectName('green'); r.addWidget(scorel); r.addWidget(QLabel('━',objectName='green')); r.addWidget(QLabel(rr)); l.addLayout(r)
        return w
    def sectors(self):
        w=self.card(); l=QVBoxLayout(w); l.setContentsMargins(16,12,16,10); l.addWidget(QLabel('SECTOR STRENGTH',objectName='title'))
        for n,v in (('Information Technology',94),('Pharma',82),('Financial Services',76),('Automobile',70),('FMCG',65),('Metals',58),('Energy',54)):
            r=QHBoxLayout(); r.addWidget(QLabel(n)); bar=QLabel('━━━━━━━━'); bar.setObjectName('green'); r.addWidget(bar); x=QLabel(str(v)); x.setObjectName('green'); r.addWidget(x); l.addLayout(r)
        return w
    def heatmap(self):
        w=self.card(); l=QVBoxLayout(w); l.setContentsMargins(16,12,16,10); l.addWidget(QLabel('MARKET HEATMAP',objectName='title')); g=QGridLayout()
        for i,(s,c) in enumerate((('RELIANCE\n+2.45%','#09733e'),('HDFCBANK\n+1.78%','#0a6a39'),('TCS\n+0.85%','#076234'),('INFY\n+1.25%','#07663a'),('ICICIBANK\n+1.32%','#08733f'),('SBIN\n-0.45%','#77272e'),('HINDUNILVR\n+0.65%','#0b6137'),('ITC\n+0.35%','#0b6137'),('BHARTIARTL\n+1.12%','#08713d'),('AXISBANK\n-0.33%','#702830'))):
            x=QLabel(s); x.setAlignment(Qt.AlignCenter); x.setStyleSheet(f'background:{c}; border-radius:3px; font-size:13px; font-weight:700;'); g.addWidget(x,i//3,i%3)
        l.addLayout(g); return w
    def panel(self,title,rows):
        w=self.card(); l=QVBoxLayout(w); l.setContentsMargins(16,12,16,10); l.addWidget(QLabel(title,objectName='title'))
        for text in rows: l.addWidget(QLabel(text,objectName='muted'))
        l.addStretch(); return w
    def summary(self): return self.panel('SCANNER SUMMARY',['◉  128 TOTAL','● Strong Buy    45 (35%)','● Buy             52 (41%)','● Watch         18 (14%)','● Avoid           5 (4%)'])
    def movers(self): return self.panel('PRICE MOVERS',['TOP GAINERS','NBCC (India)       +8.45%','Zydus Lifesciences +6.76%','Tata Power         +5.62%','IRCTC              +4.20%'])
    def alerts(self): return self.panel('ALERTS',['HAL   Price above resistance','BEL   High volume breakout','TATAMOTORS  Bullish pattern','ICICIBANK  Price above EMA 20'])
    def news(self): return self.panel('RECENT NEWS',['RBI keeps repo rate unchanged','India GDP grows 7.4% in Q4','FII inflows continue','Crude oil prices fall'])
