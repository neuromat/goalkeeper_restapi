#if UNITY_STANDALONE || UNITY_EDITOR
using UnityEngine;
using System.Collections;
using System.Collections.Generic;
using System;
using System.IO;
using System.Linq;
using System.Threading;
using Newtonsoft.Json;


public class SendOfflineToServer : MonoBehaviour
{
    private string dataPath;
    List<string> FilePaths = new List<string>();

    // Verifica se existem arquivos a serem enviados ao banco de dados
    public List<string> checkFiles()
    {
        DirectoryInfo dir = new DirectoryInfo(dataPath);
        FileInfo[] files = dir.GetFiles();

        foreach (FileInfo fileTemp in files)
        {
            if (fileTemp.Name.Contains("Plays_") && fileTemp.Name.Contains(".csv") && !fileTemp.Name.Contains("meta"))
            {
                FilePaths.Add(dataPath + "/" + fileTemp.Name);
            }
        }

        return FilePaths;
    }

    // A partir de um arquivo csv, verifica o status da jogada e envia as que ainda não foram enviadas à base
    public void SendFromCSVToDB(string path, out string playertoken, out int nivel)
    {
        var csv = new List<RandomEvent>();
        string[] lines = File.ReadAllLines(path);

        playertoken = lines[0].Split(',')[1];
        var game_phase = Convert.ToInt32(lines[1].Split(',')[1]);
        nivel = Convert.ToInt32(lines[2].Split(',')[1]);

        Debug.Log(playertoken+":"+game_phase+":"+nivel);

        lines = lines.Skip(4).ToArray();

        string[] line_aux;
        bool status = false;
        foreach (string line in lines)
        {
            line_aux = line.Split(',');

            RandomEvent evento = new RandomEvent();
            evento.resultInt = Convert.ToInt32(line_aux[1]);
            evento.ehRandom = Convert.ToChar(line_aux[2]);
            evento.optionChosenInt = Convert.ToInt32(line_aux[3]);
            evento.correct = Convert.ToBoolean(line_aux[4]);
            evento.time = Convert.ToSingle(line_aux[5]);
            evento.pauseTime = Convert.ToSingle(line_aux[6]);
            evento.realTime = Convert.ToSingle(line_aux[7]);
            evento.sendedToDB = Convert.ToBoolean(line_aux[8]);
            if (!evento.sendedToDB)
            {
                status = RegistrarJogada(playertoken, game_phase, Convert.ToInt32(line_aux[0]), evento);
            }
            Debug.Log(status);
        }
    }

    // Envia a jogada para a base através do Django Rest API
    public bool RegistrarJogada(string token, int phase, int move, RandomEvent evento)
    {
        Dictionary<string, object> dictObj = new Dictionary<string, object>();
        dictObj.Add("game_phase", phase);
        dictObj.Add("move", move);
        dictObj.Add("waited_result", evento.resultInt);
        dictObj.Add("is_random", evento.ehRandom);
        dictObj.Add("option_chosen", evento.optionChosenInt);
        dictObj.Add("correct", evento.correct);
        dictObj.Add("movement_time", evento.time);
        dictObj.Add("time_running", evento.realTime);
        dictObj.Add("pause_time", evento.pauseTime);

        string jsonObj = JsonConvert.SerializeObject(dictObj);
        var encoding = new System.Text.UTF8Encoding();
        Dictionary<string, string> postHeader = new Dictionary<string, string>();
        postHeader.Add("Content-Type", "application/json");
        postHeader.Add("Authorization", "Token " + token);

        var request = new WWW("localhost:8000/api/results/", encoding.GetBytes(jsonObj), postHeader);
        //StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }
        return request.responseHeaders.ContainsKey("STATUS");
    }

    public void UpdateLevelofPlayer(int nivel, int nivel_player, string token)
    {
        int player_level_name = GetLevel(nivel_player)[0].name;
        int game_level_name = nivel;

        if (game_level_name >= player_level_name)
        {
            player_level_name += game_level_name;

            List<LoadStages.LevelJson> new_level = GetLevel(level_name: player_level_name);
            if (new_level.Count > 0)
            {
                // Atualizar o nível dentro do jogo
                PlayerInfo.level = new_level[0].id;

                // Atualizar o n[ivel dentro da base
                UpdatePlayerLevelinDB(new_level[0].id, token);
            }
        }
    }

    public void UpdatePlayerLevelinDB(int nivel_player, string token)
    {
        string address = string.Format("localhost:8000/api/setplayerlevel?format=json&token={0}&nivel={1}", token, nivel_player);
        var request = new WWW(address);

        StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }
    }

    public List<LoadStages.LevelJson> GetLevel(int? level_id = null, int? level_name = null)
    {
        string address = "localhost:8000/api/getlevel?format=json";
        if (level_id != null)
        {
            address = address + string.Format("&id={0}", level_id);
        }
        if (level_name != null)
        {
            address = address + string.Format("&name={0}", level_name);
        }

        var request = new WWW(address);

        StartCoroutine(WaitForWWW(request));
        while (!request.isDone) { }

        var ObjList = new List<LoadStages.LevelJson>();
        ObjList = JsonConvert.DeserializeObject<List<LoadStages.LevelJson>>(request.text);
        return ObjList;
    }

    IEnumerator WaitForWWW(WWW www)
    {
        yield return www;
    }

    void Start()
    {
        dataPath = Application.dataPath + "/ResultsBk";

        // Se há arquivos a serem enviados, faz-se isso primeiro
        if (checkFiles().Count > 0)
        {
            foreach (string FilePath in FilePaths)
            {
                // Ler o caminho do arquivo e enviar as jogadas através da função SendFromCSVToDB
                string token;
                int nivel;
                SendFromCSVToDB(FilePath, out token, out nivel);
                Debug.Log("Enviou?");

                // Chamar a função que verifica se é necessário alterar o nível do jogador
                if (token == PlayerInfo.token)
                {
                    UpdateLevelofPlayer(nivel, PlayerInfo.level, token);
                }

                // Deletar o arquivo já lido e enviado
                File.Delete(FilePath);
            }
        }
    }
}
#endif