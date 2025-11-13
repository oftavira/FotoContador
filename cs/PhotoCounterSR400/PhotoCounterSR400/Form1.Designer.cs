namespace PhotoCounterSR400
{
    partial class Form1
    {
        /// <summary>
        /// Variable del diseñador necesaria.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Limpiar los recursos que se estén usando.
        /// </summary>
        /// <param name="disposing">true si los recursos administrados se deben desechar; false en caso contrario.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Código generado por el Diseñador de Windows Forms

        /// <summary>
        /// Método necesario para admitir el Diseñador. No se puede modificar
        /// el contenido de este método con el editor de código.
        /// </summary>
        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            this.BtPortSerch = new System.Windows.Forms.Button();
            this.BtConnexion = new System.Windows.Forms.Button();
            this.CbPorts = new System.Windows.Forms.ComboBox();
            this.SpSerialPort = new System.IO.Ports.SerialPort(this.components);
            this.BtInitialization = new System.Windows.Forms.Button();
            this.label1 = new System.Windows.Forms.Label();
            this.TxtLI = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.TxtLF = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.TxtSV = new System.Windows.Forms.TextBox();
            this.label4 = new System.Windows.Forms.Label();
            this.TxtTP = new System.Windows.Forms.TextBox();
            this.label5 = new System.Windows.Forms.Label();
            this.LbPeriodos = new System.Windows.Forms.Label();
            this.label6 = new System.Windows.Forms.Label();
            this.TxtEscala = new System.Windows.Forms.TextBox();
            this.progressBar1 = new System.Windows.Forms.ProgressBar();
            this.BtCancel = new System.Windows.Forms.Button();
            this.label7 = new System.Windows.Forms.Label();
            this.TxtNArchivo = new System.Windows.Forms.TextBox();
            this.BtVoltaje = new System.Windows.Forms.TextBox();
            this.TxtVoltaje = new System.Windows.Forms.Label();
            this.BtVoltageSweep = new System.Windows.Forms.Button();
            this.TxtVoltageStart = new System.Windows.Forms.TextBox();
            this.label8 = new System.Windows.Forms.Label();
            this.TxtVoltageEnd = new System.Windows.Forms.TextBox();
            this.label9 = new System.Windows.Forms.Label();
            this.TxtVoltageStep = new System.Windows.Forms.TextBox();
            this.label10 = new System.Windows.Forms.Label();
            this.TxtMaxIntensity = new System.Windows.Forms.TextBox();
            this.label11 = new System.Windows.Forms.Label();
            this.LbCurrentVoltage = new System.Windows.Forms.Label();
            this.LbCurrentIntensity = new System.Windows.Forms.Label();
            this.label12 = new System.Windows.Forms.Label();
            this.label13 = new System.Windows.Forms.Label();
            this.BtCancelVoltageSweep = new System.Windows.Forms.Button();
            this.SuspendLayout();
            // 
            // BtPortSerch
            // 
            this.BtPortSerch.Location = new System.Drawing.Point(12, 222);
            this.BtPortSerch.Name = "BtPortSerch";
            this.BtPortSerch.Size = new System.Drawing.Size(110, 23);
            this.BtPortSerch.TabIndex = 0;
            this.BtPortSerch.Text = "PORT SEARCH";
            this.BtPortSerch.UseVisualStyleBackColor = true;
            this.BtPortSerch.Click += new System.EventHandler(this.BtPortSerch_Click);
            // 
            // BtConnexion
            // 
            this.BtConnexion.Location = new System.Drawing.Point(304, 177);
            this.BtConnexion.Name = "BtConnexion";
            this.BtConnexion.Size = new System.Drawing.Size(90, 73);
            this.BtConnexion.TabIndex = 1;
            this.BtConnexion.Text = "CONNECT";
            this.BtConnexion.UseVisualStyleBackColor = true;
            this.BtConnexion.Click += new System.EventHandler(this.BtConnexion_Click);
            // 
            // CbPorts
            // 
            this.CbPorts.FormattingEnabled = true;
            this.CbPorts.Location = new System.Drawing.Point(128, 224);
            this.CbPorts.Name = "CbPorts";
            this.CbPorts.Size = new System.Drawing.Size(170, 21);
            this.CbPorts.TabIndex = 2;
            // 
            // SpSerialPort
            // 
            this.SpSerialPort.DataReceived += new System.IO.Ports.SerialDataReceivedEventHandler(this.DataReceived);
            // 
            // BtInitialization
            // 
            this.BtInitialization.Location = new System.Drawing.Point(304, 9);
            this.BtInitialization.Name = "BtInitialization";
            this.BtInitialization.Size = new System.Drawing.Size(90, 73);
            this.BtInitialization.TabIndex = 3;
            this.BtInitialization.Text = "Initialization";
            this.BtInitialization.UseVisualStyleBackColor = true;
            this.BtInitialization.Click += new System.EventHandler(this.BtInitialization_Click);
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(13, 12);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(131, 13);
            this.label1.TabIndex = 5;
            this.label1.Text = "Posicion inicial del barrido:";
            // 
            // TxtLI
            // 
            this.TxtLI.Location = new System.Drawing.Point(200, 9);
            this.TxtLI.Name = "TxtLI";
            this.TxtLI.Size = new System.Drawing.Size(98, 20);
            this.TxtLI.TabIndex = 6;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(13, 39);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(124, 13);
            this.label2.TabIndex = 7;
            this.label2.Text = "Posicion final del barrido:";
            // 
            // TxtLF
            // 
            this.TxtLF.Location = new System.Drawing.Point(200, 36);
            this.TxtLF.Name = "TxtLF";
            this.TxtLF.Size = new System.Drawing.Size(98, 20);
            this.TxtLF.TabIndex = 8;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(13, 69);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(156, 13);
            this.label3.TabIndex = 9;
            this.label3.Text = "Velocidad de barrido (cmE-1/s):";
            // 
            // TxtSV
            // 
            this.TxtSV.Location = new System.Drawing.Point(200, 66);
            this.TxtSV.Name = "TxtSV";
            this.TxtSV.Size = new System.Drawing.Size(98, 20);
            this.TxtSV.TabIndex = 10;
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(13, 95);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(181, 13);
            this.label4.TabIndex = 11;
            this.label4.Text = "Tiempo de duracion de cada periodo";
            // 
            // TxtTP
            // 
            this.TxtTP.Location = new System.Drawing.Point(200, 92);
            this.TxtTP.Name = "TxtTP";
            this.TxtTP.Size = new System.Drawing.Size(98, 20);
            this.TxtTP.TabIndex = 12;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(13, 177);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(103, 13);
            this.label5.TabIndex = 15;
            this.label5.Text = "Periodos esperados:";
            // 
            // LbPeriodos
            // 
            this.LbPeriodos.AutoSize = true;
            this.LbPeriodos.Location = new System.Drawing.Point(159, 177);
            this.LbPeriodos.Name = "LbPeriodos";
            this.LbPeriodos.Size = new System.Drawing.Size(0, 13);
            this.LbPeriodos.TabIndex = 16;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(13, 121);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(80, 13);
            this.label6.TabIndex = 17;
            this.label6.Text = "Escala maxima:";
            // 
            // TxtEscala
            // 
            this.TxtEscala.Location = new System.Drawing.Point(198, 118);
            this.TxtEscala.Name = "TxtEscala";
            this.TxtEscala.Size = new System.Drawing.Size(100, 20);
            this.TxtEscala.TabIndex = 18;
            // 
            // progressBar1
            // 
            this.progressBar1.Location = new System.Drawing.Point(12, 193);
            this.progressBar1.Name = "progressBar1";
            this.progressBar1.Size = new System.Drawing.Size(286, 23);
            this.progressBar1.TabIndex = 19;
            // 
            // BtCancel
            // 
            this.BtCancel.Location = new System.Drawing.Point(304, 89);
            this.BtCancel.Name = "BtCancel";
            this.BtCancel.Size = new System.Drawing.Size(90, 56);
            this.BtCancel.TabIndex = 20;
            this.BtCancel.Text = "Cancelar";
            this.BtCancel.UseVisualStyleBackColor = true;
            this.BtCancel.Click += new System.EventHandler(this.BtCancel_Click);
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(13, 147);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(146, 13);
            this.label7.TabIndex = 21;
            this.label7.Text = "Nombre del archivo de datos:";
            // 
            // TxtNArchivo
            // 
            this.TxtNArchivo.Location = new System.Drawing.Point(160, 144);
            this.TxtNArchivo.Name = "TxtNArchivo";
            this.TxtNArchivo.Size = new System.Drawing.Size(138, 20);
            this.TxtNArchivo.TabIndex = 22;
            // 
            // BtVoltaje
            // 
            this.BtVoltaje.Location = new System.Drawing.Point(123, 261);
            this.BtVoltaje.Name = "BtVoltaje";
            this.BtVoltaje.Size = new System.Drawing.Size(49, 20);
            this.BtVoltaje.TabIndex = 23;
            // 
            // TxtVoltaje
            // 
            this.TxtVoltaje.AutoSize = true;
            this.TxtVoltaje.Location = new System.Drawing.Point(12, 261);
            this.TxtVoltaje.Name = "TxtVoltaje";
            this.TxtVoltaje.Size = new System.Drawing.Size(105, 13);
            this.TxtVoltaje.TabIndex = 24;
            this.TxtVoltaje.Text = "Voltaje Discriminador";
            // 
            // BtVoltageSweep
            // 
            this.BtVoltageSweep.Location = new System.Drawing.Point(304, 256);
            this.BtVoltageSweep.Name = "BtVoltageSweep";
            this.BtVoltageSweep.Size = new System.Drawing.Size(90, 25);
            this.BtVoltageSweep.TabIndex = 25;
            this.BtVoltageSweep.Text = "BARRIDO VOLTAJE";
            this.BtVoltageSweep.UseVisualStyleBackColor = true;
            this.BtVoltageSweep.Click += new System.EventHandler(this.BtVoltageSweep_Click);
            // 
            // TxtVoltageStart
            // 
            this.TxtVoltageStart.Location = new System.Drawing.Point(123, 287);
            this.TxtVoltageStart.Name = "TxtVoltageStart";
            this.TxtVoltageStart.Size = new System.Drawing.Size(49, 20);
            this.TxtVoltageStart.TabIndex = 26;
            // 
            // label8
            // 
            this.label8.AutoSize = true;
            this.label8.Location = new System.Drawing.Point(12, 290);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(67, 13);
            this.label8.TabIndex = 27;
            this.label8.Text = "V Inicial (V):";
            // 
            // TxtVoltageEnd
            // 
            this.TxtVoltageEnd.Location = new System.Drawing.Point(123, 313);
            this.TxtVoltageEnd.Name = "TxtVoltageEnd";
            this.TxtVoltageEnd.Size = new System.Drawing.Size(49, 20);
            this.TxtVoltageEnd.TabIndex = 28;
            // 
            // label9
            // 
            this.label9.AutoSize = true;
            this.label9.Location = new System.Drawing.Point(12, 316);
            this.label9.Name = "label9";
            this.label9.Size = new System.Drawing.Size(62, 13);
            this.label9.TabIndex = 29;
            this.label9.Text = "V Final (V):";
            // 
            // TxtVoltageStep
            // 
            this.TxtVoltageStep.Location = new System.Drawing.Point(123, 339);
            this.TxtVoltageStep.Name = "TxtVoltageStep";
            this.TxtVoltageStep.Size = new System.Drawing.Size(49, 20);
            this.TxtVoltageStep.TabIndex = 30;
            // 
            // label10
            // 
            this.label10.AutoSize = true;
            this.label10.Location = new System.Drawing.Point(12, 342);
            this.label10.Name = "label10";
            this.label10.Size = new System.Drawing.Size(62, 13);
            this.label10.TabIndex = 31;
            this.label10.Text = "Paso V (V):";
            // 
            // TxtMaxIntensity
            // 
            this.TxtMaxIntensity.Location = new System.Drawing.Point(123, 365);
            this.TxtMaxIntensity.Name = "TxtMaxIntensity";
            this.TxtMaxIntensity.Size = new System.Drawing.Size(49, 20);
            this.TxtMaxIntensity.TabIndex = 32;
            // 
            // label11
            // 
            this.label11.AutoSize = true;
            this.label11.Location = new System.Drawing.Point(12, 368);
            this.label11.Name = "label11";
            this.label11.Size = new System.Drawing.Size(105, 13);
            this.label11.TabIndex = 33;
            this.label11.Text = "Intensidad Máx (u.a):";
            // 
            // LbCurrentVoltage
            // 
            this.LbCurrentVoltage.AutoSize = true;
            this.LbCurrentVoltage.Location = new System.Drawing.Point(197, 290);
            this.LbCurrentVoltage.Name = "LbCurrentVoltage";
            this.LbCurrentVoltage.Size = new System.Drawing.Size(13, 13);
            this.LbCurrentVoltage.TabIndex = 34;
            this.LbCurrentVoltage.Text = "0";
            // 
            // LbCurrentIntensity
            // 
            this.LbCurrentIntensity.AutoSize = true;
            this.LbCurrentIntensity.Location = new System.Drawing.Point(197, 316);
            this.LbCurrentIntensity.Name = "LbCurrentIntensity";
            this.LbCurrentIntensity.Size = new System.Drawing.Size(13, 13);
            this.LbCurrentIntensity.TabIndex = 35;
            this.LbCurrentIntensity.Text = "0";
            // 
            // label12
            // 
            this.label12.AutoSize = true;
            this.label12.Location = new System.Drawing.Point(178, 290);
            this.label12.Name = "label12";
            this.label12.Size = new System.Drawing.Size(13, 13);
            this.label12.TabIndex = 36;
            this.label12.Text = "V:";
            // 
            // label13
            // 
            this.label13.AutoSize = true;
            this.label13.Location = new System.Drawing.Point(178, 316);
            this.label13.Name = "label13";
            this.label13.Size = new System.Drawing.Size(13, 13);
            this.label13.TabIndex = 37;
            this.label13.Text = "I:";
            // 
            // BtCancelVoltageSweep
            // 
            this.BtCancelVoltageSweep.Location = new System.Drawing.Point(304, 287);
            this.BtCancelVoltageSweep.Name = "BtCancelVoltageSweep";
            this.BtCancelVoltageSweep.Size = new System.Drawing.Size(90, 23);
            this.BtCancelVoltageSweep.TabIndex = 38;
            this.BtCancelVoltageSweep.Text = "CANCELAR";
            this.BtCancelVoltageSweep.UseVisualStyleBackColor = true;
            this.BtCancelVoltageSweep.Click += new System.EventHandler(this.BtCancelVoltageSweep_Click);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(401, 400);
            this.Controls.Add(this.BtCancelVoltageSweep);
            this.Controls.Add(this.label13);
            this.Controls.Add(this.label12);
            this.Controls.Add(this.LbCurrentIntensity);
            this.Controls.Add(this.LbCurrentVoltage);
            this.Controls.Add(this.label11);
            this.Controls.Add(this.TxtMaxIntensity);
            this.Controls.Add(this.label10);
            this.Controls.Add(this.TxtVoltageStep);
            this.Controls.Add(this.label9);
            this.Controls.Add(this.TxtVoltageEnd);
            this.Controls.Add(this.label8);
            this.Controls.Add(this.TxtVoltageStart);
            this.Controls.Add(this.BtVoltageSweep);
            this.Controls.Add(this.TxtVoltaje);
            this.Controls.Add(this.BtVoltaje);
            this.Controls.Add(this.TxtNArchivo);
            this.Controls.Add(this.label7);
            this.Controls.Add(this.BtCancel);
            this.Controls.Add(this.progressBar1);
            this.Controls.Add(this.TxtEscala);
            this.Controls.Add(this.label6);
            this.Controls.Add(this.LbPeriodos);
            this.Controls.Add(this.label5);
            this.Controls.Add(this.TxtTP);
            this.Controls.Add(this.label4);
            this.Controls.Add(this.TxtSV);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.TxtLF);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.TxtLI);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.BtInitialization);
            this.Controls.Add(this.CbPorts);
            this.Controls.Add(this.BtConnexion);
            this.Controls.Add(this.BtPortSerch);
            this.Icon = ((System.Drawing.Icon)(resources.GetObject("$this.Icon")));
            this.Name = "Form1";
            this.Text = "Control";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button BtPortSerch;
        private System.Windows.Forms.Button BtConnexion;
        private System.Windows.Forms.ComboBox CbPorts;
        private System.IO.Ports.SerialPort SpSerialPort;
        private System.Windows.Forms.Button BtInitialization;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox TxtLI;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox TxtLF;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox TxtSV;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox TxtTP;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Label LbPeriodos;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.TextBox TxtEscala;
        private System.Windows.Forms.ProgressBar progressBar1;
        private System.Windows.Forms.Button BtCancel;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.TextBox TxtNArchivo;
        private System.Windows.Forms.TextBox BtVoltaje;
        private System.Windows.Forms.Label TxtVoltaje;
        private System.Windows.Forms.Button BtVoltageSweep;
        private System.Windows.Forms.TextBox TxtVoltageStart;
        private System.Windows.Forms.Label label8;
        private System.Windows.Forms.TextBox TxtVoltageEnd;
        private System.Windows.Forms.Label label9;
        private System.Windows.Forms.TextBox TxtVoltageStep;
        private System.Windows.Forms.Label label10;
        private System.Windows.Forms.TextBox TxtMaxIntensity;
        private System.Windows.Forms.Label label11;
        private System.Windows.Forms.Label LbCurrentVoltage;
        private System.Windows.Forms.Label LbCurrentIntensity;
        private System.Windows.Forms.Label label12;
        private System.Windows.Forms.Label label13;
        private System.Windows.Forms.Button BtCancelVoltageSweep;
    }
}