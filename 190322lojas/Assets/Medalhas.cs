using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Medalhas : MonoBehaviour {

	[SerializeField]

	public GameObject GameUICanvas;
	public GameObject QuadroMedalhas;


	public void PainelPremios () {
		StartCoroutine (PainelPremiosOn ());
	}


	IEnumerator PainelPremiosOn() {

		QuadroMedalhas.SetActive (true);
		//GameUICanvas.SetActive (true);

		yield return new WaitForSeconds (2);	

	}



	public void SairPainelPremios () {
		StartCoroutine (PainelPremiosOff ());
	}


	IEnumerator PainelPremiosOff() {

		QuadroMedalhas.SetActive (false);
		GameUICanvas.SetActive (true);

		yield return new WaitForSeconds (2);	

	}

	// Use this for initialization
	void Start () {
		
	}
	
	// Update is called once per frame
	void Update () {
		
	}
}
