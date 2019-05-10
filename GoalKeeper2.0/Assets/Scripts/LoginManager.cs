using UnityEngine;
using UnityEngine.UI;
using System;
using System.Collections;
using System.Collections.Generic;
using Npgsql;

public class LoginManager : MonoBehaviour {
	//	private const string Login = "vei";
	//	private const string Pass = "1020";
	private NpgsqlConnection conn = new NpgsqlConnection("Server=200.144.254.136;Port=54321;User Id=inres;Password=x1y2z3d4e5f6g7h8;Database=goleiro;SSL=true");

	[SerializeField]
	private InputField usuarioField=null;
	[SerializeField]
	private InputField senhaField = null;
	[SerializeField]
	private Text feedbackmsg = null;
	[SerializeField]
	private Toggle rememberData = null;

	// Use this for initialization
	void Start () {
		if (PlayerPrefs.HasKey ("lembra") && PlayerPrefs.GetInt ("lembra") == 1) {
			usuarioField.text = PlayerPrefs.GetString ("rememberUser"); 
			senhaField.text = PlayerPrefs.GetString ("rememberSenha"); 
		} 
	}

	bool OpenConn()
	{
		if ((conn != null) && (conn.State != System.Data.ConnectionState.Closed)) {    
			//CloseConn ();  passsssss....
			print("Conexao aberta!!!");
			return true;
		} else {
			try {               
				conn.Open ();
				return true;
			} catch (Exception exp) {                
				Debug.Log ("Connection Error opening: " + exp);
				return false;
			}
	    }
	}

	public void CloseConn()
	{
		try
		{
			conn.Close();
		}
		catch (Exception exp)
		{
			Debug.Log("Connection Error closing: "+ exp);
		}
	}

	public void FazerLogin () {
		string usuario = usuarioField.text;
		print (usuario);
		string senha = senhaField.text;
		print (senha);

		if (rememberData.isOn){
			PlayerPrefs.SetInt ("lembra",1);
			PlayerPrefs.SetString ("rememberUser",usuario);
			PlayerPrefs.SetString ("rememberSenha",senha);
		}



		//		if ((conn != null) && (conn.State != System.Data.ConnectionState.Closed)) {
		//			int meuNumero = Convert.ToInt32 (Console.ReadLine ());
		//			print(meuNumero + " foi pressionada.");
		//		}


		int meuNumero = Convert.ToInt32 (Console.ReadLine ());
		print(meuNumero + " foi pressionada.");

		// Terceiro passo: Conexão e envio ao banco de dados
		if (!this.OpenConn ()) {
			// testando se a conexão foi aberta.
			return;
		}

		//		string query = "select * from users where nome = '" + usuario + "' and senha = '" + senha + "'";
		string query = "select * from gameconfig";

		try {
			NpgsqlCommand cmd = new NpgsqlCommand (query, conn);

			NpgsqlDataReader reader = cmd.ExecuteReader();
			while(reader.Read()) {
				string userName = (string) reader["playeralias"];
				string passWD = (string) reader["status"];
				Console.WriteLine("Info: " +
					userName + " " + passWD);

				//			if (reader.HasRows)
				//			{
				// 			 feedbackmsg.CrossFadeAlpha (100f, 0f, false);
				//			 feedbackmsg.color = Color.green;
				//			 print ("Login realizado com sucesso\nCarregando jogo...");
				//			 feedbackmsg.text = "Login realizado com sucesso\nCarregando jogo...";
				// 			 CarregaScene();
				//			} else {
				//			 feedbackmsg.CrossFadeAlpha (100f, 0f, false);
				//			 feedbackmsg.color = Color.red;
				//			 print ("Deu ruim...");
				//			 feedbackmsg.text = "Usuário ou senha inválidos!!!";
				//			 feedbackmsg.CrossFadeAlpha (0f, 2f, false);
				//			 usuarioField.text = "";
				//			 senhaField.text = "";
				//			}


			}
			// clean up
			reader.Close();
		} catch (NpgsqlException e) {
			//			Debug.Log("ExecuteQuery problem:" + conn.FullState);	  
			if (e.BaseMessage.Contains ("pkey")) {
				conn.Close ();
			}
			Debug.Log("General failure at PostgreSQL\n" + e.BaseMessage);  
		}

		this.CloseConn ();
	}

}

