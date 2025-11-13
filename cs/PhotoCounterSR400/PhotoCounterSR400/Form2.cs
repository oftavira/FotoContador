using PhotoCounterSR400.Class;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace PhotoCounterSR400
{
    public partial class Form2 : Form
    {
        Graphics gD;
        Pen pen = new Pen(Color.Yellow);
        Pen pdata = new Pen(Color.White);
        Pen voltageSweepPen = new Pen(Color.Red);
        Datos datos;
        List<double> listy,listx;
        List<PointF> voltageSweepPoints;
        public double xWidth = 0;
        public double yHeight = 0;
        public float x0, y0;
        public int data=0, time=0;
        private bool isVoltageSweepMode = false;

        /*Forma donde se grafican los datos obtenidos para su visualización en tiempo real del experimento y poder hacer
         * rectificaciones despues del conteo, ya mensionado en antioridad, se desa que se autoescale los valores, con el
         * objetivo de ser practicamente automatico el uso de la herramienta.
         */

        private void lbTime_TextChanged(object sender, EventArgs e)
        {
            if (!isVoltageSweepMode)
            {
                if (float.Parse(lbTime.Text) <= -1 * xWidth)
                {
                    gD.Clear(Color.Black);
                    PointF[] referencia =
                    {
                        new PointF(x0,10),
                        new PointF(x0,panel1.Height),
                        new PointF(0,y0),
                        new PointF(panel1.Width-10,y0)
                    };
                    gD.DrawLines(pen, referencia);
                }
                else
                {
                    data = (int)(y0 - float.Parse(lbData.Text));
                    time = (int)(x0 + float.Parse(lbTime.Text));
                    gD.DrawRectangle(pdata, time, data, 1, 1);
                }
            }
        }

        private void panel1_Paint(object sender, PaintEventArgs e)
        {
            PointF[] referencia =
            {
                new PointF(x0,10),
                new PointF(x0,panel1.Height),
                new PointF(0,y0),
                new PointF(panel1.Width-10,y0)
            };
            gD.DrawLines(pen, referencia);

            // Draw voltage sweep points if in voltage sweep mode
            if (isVoltageSweepMode && voltageSweepPoints != null && voltageSweepPoints.Count > 1)
            {
                gD.DrawLines(voltageSweepPen, voltageSweepPoints.ToArray());
            }
        }

        public Form2()
        {
            InitializeComponent();
            voltageSweepPoints = new List<PointF>();
        }


        private void Form2_Load(object sender, EventArgs e)
        {
            datos = new Datos();
            xWidth = panel1.Width - 25;
            yHeight = panel1.Height - 20;
            x0 = 10;
            y0 = panel1.Height - 10;
            gD = panel1.CreateGraphics();
           
        }

        public void drawLine(double x, double y, int periodo,int escala)
        {
            isVoltageSweepMode = false;
            lbData.Text = (((y /escala) * yHeight)).ToString();
            lbTime.Text = (((x / periodo) * xWidth)).ToString();
        }

        public void drawVoltageSweepPoint(double voltage, double intensity, double startVoltage, double endVoltage, double maxIntensity)
        {
            isVoltageSweepMode = true;
            
            // Calculate normalized coordinates
            float x = (float)(x0 + ((voltage - startVoltage) / (endVoltage - startVoltage)) * (panel1.Width - 20));
            float y = (float)(y0 - (intensity / maxIntensity) * (panel1.Height - 20));
            
            // Add point to list
            voltageSweepPoints.Add(new PointF(x, y));
            
            // Redraw the panel
            panel1.Invalidate();
        }

        public void ClearVoltageSweep()
        {
            voltageSweepPoints.Clear();
            gD.Clear(Color.Black);
            panel1.Invalidate();
        }
    }
}