using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace PhotoCounterSR400.Class
{
    public class Datos
    {
        public List<double> foton,time;
        public double period,li;
        public float i,maxData=0;
        public string name;
        public List<string> character,fotoneV;
        // TODO real implementation: Add voltage sweep data storage
        public List<string> voltageSweepData;

        /*Clase donde se manipulan los datos para su uso posterior, aquí es donde se guardan y borran los datos despues
         * de un conteo exitoso, se desa que en esta clase se puedan ordenar los datos de manera automatica ya que la 
         * grafica se tiene que autoescalar.
         */

        public Datos()
        {
            fotoneV = new List<string>();
            foton = new List<double>();
            time = new List<double>();
            character = new List<string>();
            voltageSweepData = new List<string>();
        }
        public void saveData(float counter, float timer)
        {
            try
            {
                if (maxData < counter)
                {
                    maxData = counter + 20;
                }
                foton.Add(counter);
                time.Add(timer);
                //fotoneV.Add(Math.Round((li / 8065.5) + (timer * period / 8065.5), 5) + "," + counter);
                fotoneV.Add(Math.Round(li + (timer * period), 5) + "," + counter);

            } catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString());
            }
        }

        // TODO real implementation: Add method to save voltage sweep data
        public void SaveVoltageSweepData(double voltage, double intensity)
        {
            voltageSweepData.Add($"{voltage:F3},{intensity:F0}");
        }

        //Se guardan todos los datos en un documento de formato text para su uso posterior 
        public void Save()
        {
            string path = @"C:\Users\Public\FotoCounterData\";
            if (!Directory.Exists(path)){
                Directory.CreateDirectory(path);
            }

            StreamWriter sw = new StreamWriter(path+name+".txt");
            DateTime localDate = DateTime.Now;
            try
            {
                foreach (string data in fotoneV)
                {
                    sw.WriteLine(data);
                }
                sw.WriteLine("Instituto Politecnico Nacional");
                sw.WriteLine("Escuela Superior de Física y Matemática");
                sw.WriteLine("Laboratorio de Física Avanzada");
                sw.WriteLine("Fecha de experimento (México): " + localDate.ToString("MM/dd/yyyy HH:mm"));
                sw.WriteLine("Condiciones de barrido");
                foreach (string character in character)
                {
                    sw.WriteLine(character);
                }
                sw.Close();
                fotoneV.Clear();
                character.Clear();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString());
            }
        }

        // TODO real implementation: Add method to save voltage sweep to separate file
        public void SaveVoltageSweep(string filename)
        {
            string path = @"C:\Users\Public\FotoCounterData\";
            if (!Directory.Exists(path)){
                Directory.CreateDirectory(path);
            }

            StreamWriter sw = new StreamWriter(path + filename + "_voltage_sweep.txt");
            DateTime localDate = DateTime.Now;
            try
            {
                sw.WriteLine("Voltage (V), Intensity (u.a)");
                foreach (string data in voltageSweepData)
                {
                    sw.WriteLine(data);
                }
                sw.WriteLine("Instituto Politecnico Nacional");
                sw.WriteLine("Escuela Superior de Física y Matemática");
                sw.WriteLine("Laboratorio de Física Avanzada");
                sw.WriteLine("Fecha de experimento (México): " + localDate.ToString("MM/dd/yyyy HH:mm"));
                sw.WriteLine("Barrido de Voltaje - Datos de Intensidad vs Voltaje");
                sw.Close();
                voltageSweepData.Clear();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString());
            }
        }

        public void CondicionalValues(String values)
        {
            character.Add(values);
        }
        public void EliminarDatos()
        {
            string path = @"C:\Users\Public\FotoCounterData\";
            StreamWriter sw = new StreamWriter(path + name + ".txt");
            try {
                if (File.Exists(path + name + ".txt"))
                {
                    sw.Close();
                    File.Delete(path + name + ".txt");
                }

            } catch (Exception ex)
            {
                MessageBox.Show(ex.Message.ToString());
            }
        }
        //Sección donde se desea hacer el autoescalado de la grafica, aun no se usa pues no funciona.
        //Aquí es donde se requiere trabajar (u.u)000
        public List<double> AutoDataYRef(double height)
        {
            foreach (int i in foton)
            {
                foton[i] = (foton[i]/maxData) * height;
            }
            return foton;
        }
        public List<double> AutoDataXRef(double width, float periodo)
        {
            foreach(int i in time)
            {
                time[i] = (time[i] / periodo) * width;
            }
            return time;
        }
    }

}