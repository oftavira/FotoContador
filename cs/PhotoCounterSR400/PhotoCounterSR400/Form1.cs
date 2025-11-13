using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO.Ports;
using System.Windows.Forms;
using PhotoCounterSR400.Class;

namespace PhotoCounterSR400
{
    public partial class Form1 : Form
    {
        Form2 graphic;
        Datos datos;
        DialogResult result;
        private string strBufferIn;
        private delegate void accessDelegate(string action);
        public float data = 0, time = 0,voltaje;
        public int unicode = 13, periodos=0;
        public char character;
        public string text;
        public double tp,li,lf,sv,lect;
        private BackgroundWorker voltageSweepWorker;
        private bool isVoltageSweepRunning = false;

        public Form1()
        {
            InitializeComponent();
            InitializeVoltageSweepWorker();
        }

        private void InitializeVoltageSweepWorker()
        {
            voltageSweepWorker = new BackgroundWorker();
            voltageSweepWorker.WorkerReportsProgress = true;
            voltageSweepWorker.WorkerSupportsCancellation = true;
            voltageSweepWorker.DoWork += VoltageSweepWorker_DoWork;
            voltageSweepWorker.ProgressChanged += VoltageSweepWorker_ProgressChanged;
            voltageSweepWorker.RunWorkerCompleted += VoltageSweepWorker_RunWorkerCompleted;
        }

        private void VoltageSweepWorker_DoWork(object sender, DoWorkEventArgs e)
        {
            // TODO real implementation: Replace simulation with actual device communication
            // This simulates a voltage sweep with intensity measurements
            
            double startVoltage = double.Parse(TxtVoltageStart.Text);
            double endVoltage = double.Parse(TxtVoltageEnd.Text);
            double stepVoltage = double.Parse(TxtVoltageStep.Text);
            int points = (int)Math.Abs((endVoltage - startVoltage) / stepVoltage) + 1;
            
            for (int i = 0; i < points; i++)
            {
                if (voltageSweepWorker.CancellationPending)
                {
                    e.Cancel = true;
                    return;
                }
                
                double currentVoltage = startVoltage + (i * stepVoltage);
                
                // TODO real implementation: Replace with actual device measurement
                // Simulating intensity measurement - this would be replaced with actual device reading
                double simulatedIntensity = SimulateIntensityMeasurement(currentVoltage);
                
                // Report progress with voltage and intensity
                voltageSweepWorker.ReportProgress(i, new VoltageSweepData 
                { 
                    Voltage = currentVoltage, 
                    Intensity = simulatedIntensity,
                    Progress = (i * 100) / points
                });
                
                System.Threading.Thread.Sleep(100); // Simulate measurement time
            }
        }

        private double SimulateIntensityMeasurement(double voltage)
        {
            // TODO real implementation: Replace with actual device reading
            // Simulating a typical photodiode response curve
            double maxIntensity = 1000; // Maximum expected intensity
            double peakVoltage = 2.5; // Voltage where peak intensity occurs
            
            // Gaussian-like response for simulation
            double intensity = maxIntensity * Math.Exp(-Math.Pow(voltage - peakVoltage, 2) / 2.0);
            
            // Add some noise for realism
            Random rand = new Random();
            intensity += rand.NextDouble() * 50 - 25; // ±25 noise
            
            return Math.Max(0, intensity);
        }

        private void VoltageSweepWorker_ProgressChanged(object sender, ProgressChangedEventArgs e)
        {
            if (e.UserState is VoltageSweepData sweepData)
            {
                // Update the graph with voltage vs intensity
                graphic.drawVoltageSweepPoint(sweepData.Voltage, sweepData.Intensity, 
                    double.Parse(TxtVoltageStart.Text), double.Parse(TxtVoltageEnd.Text),
                    double.Parse(TxtMaxIntensity.Text));
                
                // Update progress
                progressBar1.Value = (int)sweepData.Progress;
                
                // Update labels
                LbCurrentVoltage.Text = sweepData.Voltage.ToString("F3");
                LbCurrentIntensity.Text = sweepData.Intensity.ToString("F0");
            }
        }

        private void VoltageSweepWorker_RunWorkerCompleted(object sender, RunWorkerCompletedEventArgs e)
        {
            isVoltageSweepRunning = false;
            
            if (e.Cancelled)
            {
                MessageBox.Show("Barrido de Voltaje cancelado", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            else
            {
                MessageBox.Show("Barrido de Voltaje completado", "", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
            }
            
            // Reset UI
            BtVoltageSweep.Text = "INICIAR BARRIDO";
            BtCancelVoltageSweep.Enabled = false;
            progressBar1.Value = 0;
            
            // Re-enable controls
            EnableVoltageSweepControls(true);
            BtConnexion.Enabled = true;
        }

        /*Interrupcion del programa a la espera de los datos obtenidos por el Contador de fontones, basicamente en una
         * cadena de datos, estan las cuentas obtenidas por el equipo, agregando que dentro del método invocamos a la
         * clase Class1 para guardar los datos obtenidos para su uso, ademas, tambien se invoca la forma From2 para 
         * graficar los datos.
         */ 
        private void AccesFrom(string action)
        {
            strBufferIn = action;
            float.TryParse(strBufferIn, out data);

            //Se guardan tanto los datos como el tiempo.
            datos.saveData(data, time);

            //Datos que se van a graficar.
            graphic.drawLine(Math.Abs(time), data, periodos, Int32.Parse(TxtEscala.Text));

            //Manipulación de los elementos de la forma Form1 para volver a inicalizar el conteo.
            progressBar1.Value = (int)((Math.Abs(time)/periodos)*100);
            if (Math.Abs(time) == periodos)
            {
                MessageBox.Show("Conteo Exitoso", "", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                //SpSerialPort.Write("RC0" + text);
                time = 0;
                progressBar1.Value = 0;
                datos.Save();
                BtInitialization.Enabled = true;
                BtCancel.Enabled = false;
                BtConnexion.Enabled = true;
                TxtLF.Enabled = true;
                TxtLI.Enabled = true;
                TxtSV.Enabled = true;
                TxtTP.Enabled = true;
                BtVoltaje.Enabled = true;
                TxtEscala.Enabled = true;
                TxtNArchivo.Enabled = true;
                EnableVoltageSweepControls(true);
            }
        }
        //Método para la interrupcción para adquirir los datos en el puerto Serie
        private void InteruptionAcces(string action)
        {
            accessDelegate varAccessDelegate;
            varAccessDelegate = new accessDelegate(AccesFrom);
            object[] arg = { action };
            base.Invoke(varAccessDelegate, arg);
        }

        private void EnableVoltageSweepControls(bool enable)
        {
            TxtVoltageStart.Enabled = enable;
            TxtVoltageEnd.Enabled = enable;
            TxtVoltageStep.Enabled = enable;
            TxtMaxIntensity.Enabled = enable;
            BtVoltageSweep.Enabled = enable;
        }

        //Caracterización de los elementos que forman la forma Form1
        private void BtCancel_Click(object sender, EventArgs e)
        {

            result=MessageBox.Show("¿Desea cancelar el conteo?", "", MessageBoxButtons.YesNo, MessageBoxIcon.Exclamation);
            if (result == System.Windows.Forms.DialogResult.Yes)
            {
                //SpSerialPort.Write("RC0" + text);
                graphic.drawLine(-1, 0, 1, 1);
                time = 0;
                progressBar1.Value = 0;
                datos.EliminarDatos();
                BtInitialization.Enabled = true;
                BtConnexion.Enabled = true;
                BtVoltaje.Enabled = true;
                BtCancel.Enabled = false;
                BtVoltaje.Enabled = true;
                TxtLF.Enabled = true;
                TxtLI.Enabled = true;
                TxtSV.Enabled = true;
                TxtTP.Enabled = true;
                TxtVoltaje.Enabled = true;
                TxtEscala.Enabled = true;
                TxtNArchivo.Enabled = true;
                EnableVoltageSweepControls(true);
            }
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            datos = new Datos();
            BtConnexion.Enabled = false;
            BtCancel.Enabled = false;
            BtInitialization.Enabled = false;
            BtVoltaje.Enabled = false;
            TxtLF.Enabled = false;
            TxtLI.Enabled = false;
            TxtSV.Enabled = false;
            TxtTP.Enabled = false;
            TxtVoltaje.Enabled = false;
            TxtEscala.Enabled = false;
            TxtNArchivo.Enabled = false;
            character = (char)unicode;

            // Initialize voltage sweep defaults
            TxtVoltageStart.Text = "0";
            TxtVoltageEnd.Text = "5";
            TxtVoltageStep.Text = "0.1";
            TxtMaxIntensity.Text = "1000";
            EnableVoltageSweepControls(false);
            BtCancelVoltageSweep.Enabled = false;
        }

        private void BtPortSerch_Click(object sender, EventArgs e)
        {
            string[] avbaiblePorts = SerialPort.GetPortNames();
            CbPorts.Items.Clear();
            foreach (string simplePort in avbaiblePorts)
            {
                CbPorts.Items.Add(simplePort);
            }
            if (CbPorts.Items.Count > 0)
            {
                CbPorts.SelectedIndex = 0;
                BtConnexion.Enabled = true;
            }
            else
            {
                MessageBox.Show("NO PORT DETECTED");
                CbPorts.Items.Clear();
                CbPorts.Text = "                    ";
                BtConnexion.Enabled = false;
                BtCancel.Enabled = false;
                BtInitialization.Enabled = false;
                BtVoltaje.Enabled = false;
                TxtLF.Enabled = false;
                TxtLI.Enabled = false;
                TxtSV.Enabled = false;
                TxtTP.Enabled = false;
                TxtVoltaje.Enabled = false;
                TxtEscala.Enabled = false;
                TxtNArchivo.Enabled = false;
                EnableVoltageSweepControls(false);
            }
        }

        private void BtConnexion_Click(object sender, EventArgs e)
        {
            try
            {
                if (BtConnexion.Text == "CONNECT")
                {
                    SpSerialPort.BaudRate = 9600;
                    SpSerialPort.DataBits = 8;
                    SpSerialPort.Parity = Parity.None;
                    SpSerialPort.StopBits = StopBits.One;
                    SpSerialPort.Handshake = Handshake.None;
                    SpSerialPort.PortName = CbPorts.Text;

                    try
                    {
                        graphic = new Form2();
                        graphic.Show();
                        SpSerialPort.Open();
                        BtConnexion.Text = "DISCONNECT";
                        SpSerialPort.DiscardOutBuffer();
                        TxtLF.Enabled = true;
                        TxtLI.Enabled = true;
                        TxtSV.Enabled = true;
                        TxtTP.Enabled = true;
                        TxtVoltaje.Enabled = true;
                        TxtEscala.Enabled = true;
                        TxtNArchivo.Enabled = true;
                        BtInitialization.Enabled = true;
                        BtVoltaje.Enabled = true;
                        BtPortSerch.Enabled = false;
                        CbPorts.Enabled = false;
                        char character = (char)unicode;
                        text = character.ToString();
                        SpSerialPort.Write("RC0" + text);
                        SpSerialPort.DtrEnable = true;

                        // Enable voltage sweep controls when connected
                        EnableVoltageSweepControls(true);

                    } catch (Exception exc)
                    {
                        MessageBox.Show(exc.Message.ToString());
                    }
                } else if (BtConnexion.Text == "DISCONNECT")
                {
                    graphic.Close();
                    SpSerialPort.Close();
                    BtConnexion.Text = "CONNECT";
                    BtPortSerch.Enabled = true;
                    CbPorts.Enabled = true;
                    BtInitialization.Enabled = false;
                    BtVoltaje.Enabled = false;
                    TxtLF.Enabled = false;
                    TxtLI.Enabled = false;
                    TxtSV.Enabled = false;
                    TxtTP.Enabled = false;
                    TxtVoltaje.Enabled = false;
                    TxtEscala.Enabled = false;
                    TxtNArchivo.Enabled = false;
                    EnableVoltageSweepControls(false);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString());
            }
        }
        /*Esta acción en particular se encuentran los valores que configuran al contador de fotones para la
         * inicializacion de conteo de datos ademas de "limpiar" la grafica de la forma From2 y asi volover 
         * graficar los nuevos valores que se obtienen.
         */
        private void BtInitialization_Click(object sender, EventArgs e)
        {
            graphic.drawLine(-1, 0, 1, 1);
            BtInitialization.Enabled = false;
            BtCancel.Enabled = true;
            BtPortSerch.Enabled = false;
            BtConnexion.Enabled = false;
            BtVoltaje.Enabled = false;
            CbPorts.Enabled = false;
            TxtLF.Enabled = false;
            TxtLI.Enabled = false;
            TxtSV.Enabled = false;
            TxtTP.Enabled = false;
            TxtVoltaje.Enabled = false;
            TxtEscala.Enabled = false;
            TxtNArchivo.Enabled = false;
            EnableVoltageSweepControls(false);

            datos.CondicionalValues("Posicion inicial: "+TxtLI.Text);
            datos.CondicionalValues("Posicion final: "+TxtLF.Text);
            datos.CondicionalValues("Velocidad de barrido: "+TxtSV.Text);
            datos.CondicionalValues("Tiempo de duracion: "+TxtTP.Text);

            if (TxtLF.Text!=null && TxtLI.Text!=null)
            {
                voltaje = float.Parse(BtVoltaje.Text);
                tp = double.Parse(TxtTP.Text);
                li = double.Parse(TxtLI.Text);
                lf = double.Parse(TxtLF.Text);
                sv = double.Parse(TxtSV.Text);

                periodos = (int)(Math.Abs((li - lf) / (sv * tp)));
                lect = Math.Abs((lf - li) / 4);
                LbPeriodos.Text = periodos.ToString();
                datos.period = Math.Abs(lf - li) / periodos;
                datos.li = li;
                datos.name = TxtNArchivo.Text+".txt";

                SpSerialPort.DtrEnable = true;
                SpSerialPort.Write("CM 0; CI 0,1" + text);
                SpSerialPort.Write("SD 1;NE 0" + text);
                //SpSerialPort.Write("DT 2E-3" + text);
                SpSerialPort.Write("CP 2," + (tp * 1e5).ToString() + text);
                SpSerialPort.Write("DL 0,"+(voltaje*1e-3)+ text);
                SpSerialPort.Write("NP" + periodos.ToString() + text);
                SpSerialPort.Write("MD1,5" + text);
                SpSerialPort.Write("CR; FA" + text);
            }
            else
            {
                MessageBox.Show("El valor debera ser mayor","", MessageBoxButtons.OK, MessageBoxIcon.Error);
                BtInitialization.Enabled = true;
                BtConnexion.Enabled = true;
                BtCancel.Enabled = false;
                BtVoltaje.Enabled = true;
                TxtLF.Enabled = true;
                TxtLI.Enabled = true;
                TxtSV.Enabled = true;
                TxtTP.Enabled = true;
                TxtEscala.Enabled = true;
                TxtNArchivo.Enabled = true;
                EnableVoltageSweepControls(true);
            }
        }

        private void BtVoltageSweep_Click(object sender, EventArgs e)
        {
            if (!isVoltageSweepRunning)
            {
                // Start voltage sweep
                if (ValidateVoltageSweepParameters())
                {
                    isVoltageSweepRunning = true;
                    BtVoltageSweep.Text = "DETENER BARRIDO";
                    BtCancelVoltageSweep.Enabled = true;
                    EnableVoltageSweepControls(false);
                    BtConnexion.Enabled = false;
                    
                    // Clear previous voltage sweep data
                    graphic.ClearVoltageSweep();
                    
                    // Start background worker
                    voltageSweepWorker.RunWorkerAsync();
                }
            }
            else
            {
                // Stop voltage sweep
                voltageSweepWorker.CancelAsync();
            }
        }

        private void BtCancelVoltageSweep_Click(object sender, EventArgs e)
        {
            if (isVoltageSweepRunning)
            {
                voltageSweepWorker.CancelAsync();
            }
        }

        private bool ValidateVoltageSweepParameters()
        {
            try
            {
                double start = double.Parse(TxtVoltageStart.Text);
                double end = double.Parse(TxtVoltageEnd.Text);
                double step = double.Parse(TxtVoltageStep.Text);
                
                if (step <= 0)
                {
                    MessageBox.Show("El paso de voltaje debe ser mayor que 0", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return false;
                }
                
                if (start >= end)
                {
                    MessageBox.Show("El voltaje inicial debe ser menor que el voltaje final", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return false;
                }
                
                return true;
            }
            catch (Exception)
            {
                MessageBox.Show("Parámetros de voltaje inválidos", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }
        }

        //Método donde se "loopea" el puerto serie para la adquisición de datos.
        private void DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            time--;
            InteruptionAcces(SpSerialPort.ReadExisting());
        }
    }

    // Helper class for voltage sweep data
    public class VoltageSweepData
    {
        public double Voltage { get; set; }
        public double Intensity { get; set; }
        public double Progress { get; set; }
    }
}