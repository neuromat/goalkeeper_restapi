/************************************************************************************/
//  Module written by scaroni <renato.scaroni@gmail.com>
//
//	This Module is responsible to keep the statemachines loaded through json files 
//  as well as manage the states and to generate random probabilities associated
//  with this states
/************************************************************************************/

using UnityEngine;
using UnityEngine.UI;
using System.Collections;
using System.Collections.Generic;
using JsonFx.Json;
using System.IO;

public class StateMachine
{
	public string id;

	public int choices;

	public int limitPlays;

	public int depth;
	
	public string alphabet;
	
	public int limitValue;
	
	public Dictionary<string, JsonStateInput> states;
	
	public List<string> dicKeys;
	
	public StateMachine()
	{
		states = new Dictionary<string, JsonStateInput> ();
		dicKeys = new List<string> ();
	}
}

public class ProbCalculator : MonoBehaviour 
{
	static List<StateMachine> machines = new List<StateMachine> ();
	
	int currentStateMachineIndex;
	
	JsonStateInput currentState;
	
	List<string> transitionHistory = new List<string> ();

	private string logString = "";
	
	static private ProbCalculator _instance;
	static public ProbCalculator instance
	{
		get
		{
			if(_instance == null)
			{
				_instance = GameObject.Find("ProbCalculator").GetComponent<ProbCalculator>();
			}
			
			return _instance;
		}	
	}

	public string CurrentMachineID()
	{
		return machines [currentStateMachineIndex].id;
	}

	StateMachine LoadJson(string json)
	{



		
		JsonInput input = null;
		if(json != "")
			input = JsonReader.Deserialize<JsonInput> (json);
		
		StateMachine s = new StateMachine ();
		s.choices = input.GetChoices();
		s.depth = input.GetDepth();
		s.limitValue = input.GetLimitValue();
		s.limitPlays = input.GetLimitPlays();
		s.id = input.id;
		foreach(JsonStateInput i in input.states)
		{
			print (i.path);
			s.dicKeys.Add(i.path);
			s.states[i.path] = i;
		}
		
		return s;
	}
	
	int TwoChoices()
	{
		float r  = Random.Range(0.0f, 1.0f);
		
		string result = "0";
		
		if(r > currentState.GetProbEvent0())
		{
			result = "1";
		}
		
		string bkpResult = result;
		
		int i = -1;
		
		if(transitionHistory.Count == 0)
		{
			for(int j = 0; j < currentState.path.Length; j++)
			{
				transitionHistory.Insert(0, currentState.path[j].ToString());
			}
		}
		
		while(i < machines[currentStateMachineIndex].depth)
		{
			if (i >= 0)
				result = transitionHistory[i] + result;
			i++;
			if(machines[currentStateMachineIndex].states.ContainsKey(result))
			{
				currentState = machines[currentStateMachineIndex].states[result];
				break;
			}
		}
		
		transitionHistory.Insert(0, bkpResult);
		
		return System.Convert.ToInt16(bkpResult);
	}
	
	int ThreeCoices()
	{
		float r  = Random.Range(0.0f, 1.0f);
		
		string result = "0";
		
		if(r > currentState.GetProbEvent0() && r < currentState.GetProbEvent0() + currentState.GetProbEvent1())
		{
			result = "1";
		}
		else if(r >= currentState.GetProbEvent0() + currentState.GetProbEvent1())
		{
			result = "2";
		}
		
		string bkpResult = result;
		
		int i = -1;
		
		if(transitionHistory.Count == 0)
		{
			for(int j = 0; j < currentState.path.Length; j++)
			{
				transitionHistory.Insert(0, currentState.path[j].ToString());
			}
		}
		logString += " estado anterior: " + currentState.path;
		while(i < machines[currentStateMachineIndex].depth)
		{
			if (i >= 0)
				result = transitionHistory[i] + result;
			i++;
			if(machines[currentStateMachineIndex].states.ContainsKey(result))
			{
				currentState = machines[currentStateMachineIndex].states[result];
				break;
			}
		}

		logString += " estado atual: "+currentState.path+" resultado: "+ bkpResult+"\n";

		print (logString);

		transitionHistory.Insert(0, bkpResult);
		
		return System.Convert.ToInt16(bkpResult);
	}
	
	public int GetEvent ()
	{
		if(machines[currentStateMachineIndex].choices == 2)
		{
			return TwoChoices();
		}
		else if(machines[currentStateMachineIndex].choices == 3)
		{
			return ThreeCoices();
		}
		
		return 0;
	}

	public void GotoNextMachine()
	{
		currentStateMachineIndex ++;
	}

	public void ResetToInitialMachine()
	{
		currentStateMachineIndex = 0;
	}

	public bool CanGoToNextMachine()
	{
		if(currentStateMachineIndex < machines.Count-1)
		{
			return true;
		}
		
		return false;	
	}

	public bool GoToNextMachine()
	{
		if(currentStateMachineIndex < machines.Count)
		{
			currentStateMachineIndex ++;
			return true;
		}
		
		return false;
	}

	public int GetCurrentPlayLimit()
	{
		if(machines[currentStateMachineIndex].limitPlays != null)
			return (int)machines[currentStateMachineIndex].limitPlays;
		else
			return 0;
	}

	void SetInitState(JsonInput t)
	{
		int max = t.states.Length;
		
		int r = Random.Range(0, max);
		
		currentState = t.states[r];
	}
	
	static bool inited = false;	
	// Use this for initialization
	public void Start () 
	{
		currentStateMachineIndex = 0;
		StateMachine tmp;
		if(!inited)
		{
			if(LoadedPackage.loaded == null)
				LoadStages.LoadTreePackageFromResources();

			foreach(string s in LoadedPackage.loaded.stages)
			{
				tmp = LoadJson(s);
				if(tmp != null)
				{
					machines.Add(tmp);
				}

			}
			inited = true;
		}
		
		int max = machines[currentStateMachineIndex].states.Count;
		
		int index = Random.Range(0, max);
		
		string key = machines[currentStateMachineIndex].dicKeys[index];
		
		currentState = machines[currentStateMachineIndex].states[key];
	}
	
	public float GetCurrentLimitValue()
	{
		return (float)machines[currentStateMachineIndex].limitValue;
	}

	public int GetCurrMachineIndex()
	{
		return currentStateMachineIndex;
	}

//	public float
	
	// Update is called once per frame
	void Update () {
	
	}
}
