using System;
using System.Collections;
using System.Collections.Generic;

public class TreeJson
{
    public string id { get; set; }
    public int? limitPlays { get; set; }
    public int choices { get; set; }
    public int? depth { get; set; }
    public bool readSequ { get; set; }
    public string sequ { get; set; }
    public string sequR { get; set; }
    public int? minHits { get; set; }
    public int? minHitsInSequence { get; set; }
    public string animationTypeJG { get; set; }
    public string animationTypeOthers { get; set; }
    public bool scoreboard { get; set; }
    public string finalScoreboard { get; set; }
    public int playsToRelax { get; set; }
    public bool showHistory { get; set; }
    public double speedGKAnim{ get; set; }
    public List<JsonStateInput> states { get; set; }
}