    1 #include <draw.h>
    2 #include <draw3d.h>
    3
    4 #include <gif_tags.h>
    5 #include <gs_gp.h>
    6
    7 #include <stdio.h>
    8 #include <stdlib.h>
    9 #include <sys/fcntl.h>
   10 #include <string.h>
   11
   12 #include <fcntl.h>
   13 #include <unistd.h>
   14
   15 #include <font.h>
   16
   17 // Single byte fonts have only a single table whose offset starts after type.
   18 typedef struct {
   20     char id[7];
   22     char name[9];
   24     unsigned char width;
   26     unsigned char height;
   28     unsigned char type;
   29     // Single-byte font headers end here
   31     unsigned char table_num;
   32     struct {
   34         unsigned short start;
   36         unsigned short end;
   37     } block[];
   38 } fontx_hdr;
   39
   40 static const prim_t charprim =
   41 {
   42     PRIM_POINT, PRIM_SHADE_FLAT, DRAW_DISABLE,
   43     DRAW_DISABLE, DRAW_ENABLE, DRAW_DISABLE,
   44     PRIM_MAP_ST, PRIM_UNFIXED
   45 };
   46
   47 // These are the SJIS table ranges for character lookup
   48 static const unsigned short sjis_table[] = {
   49 0x8140,0x817e,
   50 0x8180,0x81ac,
   51 0x81b8,0x81bf,
   52 0x81c8,0x81ce,
   53 0x81da,0x81e8,
   54 0x81f0,0x81f7,
   55 0x81fc,0x81fc,
   56 0x824f,0x8258,
   57 0x8260,0x8279,
   58 0x8281,0x829a,
   59 0x829f,0x82f1,
   60 0x8340,0x837e,
   61 0x8380,0x8396,
   62 0x839f,0x83b6,
   63 0x83bf,0x83d6,
   64 0x8440,0x8460,
   65 0x8470,0x847e,
   66 0x8480,0x8491,
   67 0x849f,0x84be,
   68 0x889f,0x88fc,
   69 0x8940,0x897e,
   70 0x8980,0x89fc,
   71 0x8a40,0x8a7e,
   72 0x8a80,0x8afc,
   73 0x8b40,0x8b7e,
   74 0x8b80,0x8bfc,
   75 0x8c40,0x8c7e,
   76 0x8c80,0x8cfc,
   77 0x8d40,0x8d7e,
   78 0x8d80,0x8dfc,
   79 0x8e40,0x8e7e,
   80 0x8e80,0x8efc,
   81 0x8f40,0x8f7e,
   82 0x8f80,0x8ffc,
   83 0x9040,0x907e,
   84 0x9080,0x90fc,
   85 0x9140,0x917e,
   86 0x9180,0x91fc,
   87 0x9240,0x927e,
   88 0x9280,0x92fc,
   89 0x9340,0x937e,
   90 0x9380,0x93fc,
   91 0x9440,0x947e,
   92 0x9480,0x94fc,
   93 0x9540,0x957e,
   94 0x9580,0x95fc,
   95 0x9640,0x967e,
   96 0x9680,0x96fc,
   97 0x9740,0x977e,
   98 0x9780,0x97fc,
   99 0x9840,0x9872
  100 };
  101
  102 int fontx_load_single_krom(fontx_t *fontx)
  103 {
  104
  105     fontx_hdr *fontx_header;
  106
  107     int header_size = 17;
  108     int char_size = 15;
  109
  110     int fd = 0;
  111     int size;
  112
  113     fd = open("rom0:KROM", O_RDONLY);
  114
  115     if (fd < 0)
  116     {
  117
  118         printf("Error opening KROM font.\n");
  119         return -1;
  120
  121     }
  122
  123     // header without table pointer + size of a character * 256 characters
  124     size = header_size + char_size * 256;
  125
  126     fontx->font = (char*)malloc(size);
  127
  128     if (fontx->font == NULL)
  129     {
  130
  131         printf("Error allocating %d bytes of memory.\n", size);
  132         close(fd);
  133
  134         return -1;
  135     }
  136
  137     // Clear the memory
  138     memset(fontx->font,0,size);
  139
  140     // The offset for the ASCII characters
  141     lseek(fd, 0x198DE, SEEK_SET);
  142
  143     // 17 bytes of header and 15 bytes per 33 characters
  144     // Read in 95 characters
  145     if (read(fd,fontx->font + header_size+char_size*33, char_size*95) < 0)
  146     {
  147
  148         printf("Error reading rom0:KROM.\n");
  149
  150         free(fontx->font);
  151         close(fd);
  152
  153         return -1;
  154
  155     }
  156
  157     close(fd);
  158
  159     fontx_header = (fontx_hdr*)fontx->font;
  160
  161     // define header as single-byte font
  162     strcpy(fontx_header->id, "FONTX2");
  163     fontx_header->id[6] = '\0';
  164     strcpy(fontx_header->name, "KROM");
  165     fontx_header->name[8] = '\0';
  166
  167     fontx_header->width = 8;
  168     fontx_header->height = 15;
  169     fontx_header->type = SINGLE_BYTE;
  170
  171     // Save it as a font
  172     //fd=open("host:KROM_ascii.fnt",O_WRONLY | O_TRUNC | O_CREAT);
  173     //write(fd, fontx->font, size);
  174     //close(fd);
  175
  176     return 0;
  177
  178 }
  179
  180 int fontx_load_double_krom(fontx_t *fontx)
  181 {
  182
  183     fontx_hdr *fontx_header;
  184
  185     int size;
  186     int fd = 0;
  187
  188     // Font characteristics for double-byte font
  189     int header_size = 18;
  190     int table_num = 51;
  191     int table_size = 4;
  192     int char_size = 30;
  193     int char_num = 3489;
  194
  195     fd = open("rom0:KROM", O_RDONLY);
  196
  197     if (fd < 0)
  198     {
  199
  200         printf("Error opening KROM font.\n");
  201
  202     }
  203
  204     size = header_size + table_num*table_size +  char_num*char_size;
  205
  206     fontx->font = (char*)malloc(size);
  207
  208     if (fontx->font == NULL)
  209     {
  210
  211         printf("Error allocating memory.\n");
  212         close(fd);
  213
  214         return -1;
  215     }
  216
  217     // Clear memory
  218     memset(fontx->font,0,size);
  219
  220     // Make sure we're at the beginning
  221     lseek(fd, 0, SEEK_SET);
  222
  223     // Read in 95 characters
  224     if (read(fd, fontx->font+header_size+table_num*table_size, char_size*char_num) < 0)
  225     {
  226
  227         printf("Error reading font.\n");
  228         free(fontx->font);
  229         close(fd);
  230
  231         return -1;
  232
  233     }
  234
  235     close(fd);
  236
  237     fontx_header = (fontx_hdr*)fontx->font;
  238
  239     // define the header as double-byte font
  240     strcpy(fontx_header->id, "FONTX2");
  241     fontx_header->id[6] = '\0';
  242     strcpy(fontx_header->name, "KROM");
  243     fontx_header->name[8] = '\0';
  244
  245     fontx_header->width = 16;
  246     fontx_header->height = 15;
  247     fontx_header->type = DOUBLE_BYTE;
  248     fontx_header->table_num = table_num;
  249
  250     // Add the SJIS tables to the font
  251     memcpy(fontx->font+header_size,sjis_table,table_num*table_size);
  252
  253     // Save it as a font
  254     //fd=open("host:KROM_kanji.fnt",O_WRONLY | O_TRUNC | O_CREAT);
  255     //write(fd, fontx->font, size);
  256     //close(fd);
  257
  258     return 0;
  259
  260 }
  261
  262 int fontx_load(const char *path, fontx_t* fontx, int type, int wmargin, int hmargin, int bold)
  263 {
  264
  265
  266
  267     fontx_hdr *fontx_header = NULL;
  268
  269     if (!strcmp("rom0:KROM",path) || !strcmp("rom0:/KROM",path))
  270     {
  271         int ret = -1;
  272
  273         if (type == SINGLE_BYTE)
  274         {
  275
  276             ret = fontx_load_single_krom(fontx);
  277
  278         }
  279         else
  280         {
  281
  282             ret = fontx_load_double_krom(fontx);
  283
  284         }
  285
  286         if (ret < 0)
  287         {
  288
  289             printf("Error opening %s\n", path);
  290             return -1;
  291
  292         }
  293
  294     }
  295
  296     else
  297     {
  298         long size = 0;
  299
  300         FILE *file = fopen(path, "r");
  301
  302         if (file == NULL)
  303         {
  304
  305             printf("Error opening %s\n", path);
  306             return -1;
  307
  308         }
  309
  310         // get size of file
  311         fseek(file, 0, SEEK_END);
  312         size = ftell(file);
  313         fseek(file, 0, SEEK_SET);
  314
  315         fontx->font = (char *)malloc(size);
  316
  317         if (fontx->font == NULL)
  318         {
  319
  320             printf("Error allocating %ld bytes of memory.\n", size);
  321             fclose(file);
  322             return -1;
  323
  324         }
  325
  326         fread(fontx->font, size, 1, file);
  327
  328         fclose(file);
  329
  330     }
  331
  332     fontx_header = (fontx_hdr*)fontx->font;
  333
  334     if (strncmp(fontx_header->id, "FONTX2", 6) != 0)
  335     {
  336
  337         printf("Not FONTX2 type font!\n");
  338         free(fontx->font);
  339
  340         return -1;
  341
  342     }
  343
  344     if (fontx_header->type != type)
  345     {
  346
  347         printf("Type mismatch\n");
  348         free(fontx->font);
  349
  350         return -1;
  351
  352     }
  353
  354     // Fill in some information about the font
  355     strcpy(fontx->name,fontx_header->name);
  356
  357     fontx->rowsize = ((fontx_header->width+7)>>3);
  358     fontx->charsize = fontx->rowsize * fontx_header->height;
  359     fontx->w_margin = wmargin;
  360     fontx->h_margin = hmargin;
  361     fontx->bold = bold;
  362
  363     // This is the offset that character data starts
  364     if (fontx_header->type == SINGLE_BYTE)
  365     {
  366
  367         fontx->offset = 17;
  368
  369     }
  370     else
  371     {
  372
  373         // 17 + 1 + (number of tables * 4) bytes
  374         fontx->offset = 18 + (fontx_header->table_num * 4);
  375
  376     }
  377
  378     return 0;
  379
  380 }
  381
  382 void fontx_unload(fontx_t *fontx)
  383 {
  384
  385     if (fontx->font != NULL)
  386     {
  387
  388         free(fontx->font);
  389
  390     }
  391
  392 }
  393
  394 char *fontx_get_char(fontx_t* fontx, unsigned short c)
  395 {
  396
  397     unsigned int i;
  398
  399     int table = -1;
  400     int table_offset = 0;
  401
  402     fontx_hdr *fontx_header;
  403
  404     if (fontx->font == NULL)
  405     {
  406
  407         printf("Font data not loaded.\n");
  408         return NULL;
  409
  410     }
  411
  412     fontx_header = (fontx_hdr*)fontx->font;
  413
  414     if ((fontx_header->type == SINGLE_BYTE) && (c <= 0xFF))
  415     {
  416
  417         return (fontx->font + (fontx->offset + c * fontx->charsize));
  418
  419     }
  420
  421     for (i = 0; i < fontx_header->table_num; i++)
  422     {
  423
  424         if ((fontx_header->block[i].start <= c) && (fontx_header->block[i].end >= c))
  425         {
  426
  427                 table = i;
  428                 break;
  429
  430         }
  431     }
  432
  433     // If table not found
  434     if (table < 0)
  435     {
  436
  437         return NULL;
  438
  439     }
  440
  441     for (i = 0; i < (unsigned int)table; i++)
  442     {
  443
  444         table_offset += fontx_header->block[i].end - fontx_header->block[i].start;
  445
  446     }
  447
  448     table_offset = table_offset + table + ( c - fontx_header->block[table].start);
  449
  450     return (fontx->font + (fontx->offset + table_offset*fontx->charsize));
  451
  452 }
  453
  454 // draws a single byte
  455 u64 *draw_fontx_row(u64 *dw, unsigned char byte, int x, int y, int z, int bold)
  456 {
  457
  458     unsigned char mask = 0x80;
  459
  460     int i;
  461     int px = 0;
  462
  463     // for each bit in a row
  464     for (i=0;i<8;i++)
  465     {
  466
  467         // if there's a bit
  468         if (byte & mask)
  469         {
  470
  471             *dw++ = GS_SET_XYZ((x+(i<<4)) + 32768,y+32768,z);
  472             px = 1;
  473
  474         }
  475         else
  476         {
  477
  478             if (bold && px)
  479                 *dw++ = GS_SET_XYZ((x+(i<<4)) + 32768,y+32768,z);
  480
  481             px = 0;
  482
  483         }
  484
  485         mask >>= 1;
  486
  487     }
  488
  489     // Add some boldness to the last pixel in a row
  490     if (bold && px)
  491     {
  492
  493         *dw++ = GS_SET_XYZ((x+(i<<4)) + 32768,y+32768,z);
  494
  495     }
  496
  497     return dw;
  498
  499 }
  500
  501 qword_t *draw_fontx_char(qword_t *q, unsigned short c, vertex_t *v0, fontx_t *fontx)
  502 {
  503
  504     u64 pdw;
  505     u64 *dw = (u64 *)q;
  506
  507     char *char_offset;
  508     int i, j;
  509     int x,y,z;
  510     int xi;
  511
  512     x = ftoi4(v0->x);
  513     y = ftoi4(v0->y);
  514     z = v0->z;
  515
  516     fontx_hdr* fontx_header = (fontx_hdr*)fontx->font;
  517
  518     char_offset = fontx_get_char(fontx,c);
  519
  520     if (!char_offset)
  521     {
  522
  523         return q;
  524
  525     }
  526
  527     for (i=0;i<fontx_header->height;i++)
  528     {
  529         int yi;
  530
  531         // Increment one row down
  532         yi = y + (i << 4);
  533
  534         for (j=0;j < fontx->rowsize;j++)
  535         {
  536
  537             // Increment one row right
  538             xi = x + (j << 7);
  539             dw = draw_fontx_row(dw,char_offset[(i*fontx->rowsize) + j],xi,yi,z,fontx->bold);
  540
  541         }
  542
  543     }
  544
  545     if ((u32)dw % 16)
  546     {
  547
  548         pdw = *(dw-1);
  549         *dw++ = pdw;
  550
  551     }
  552
  553     q = (qword_t*)dw;
  554
  555     return q;
  556
  557 }
  558
  559 qword_t *fontx_print_ascii(qword_t *q, int context, const unsigned char *str, int alignment, const vertex_t *v0, const color_t *c0, fontx_t *fontx)
  560 {
  561
  562     int i,j;
  563
  564     fontx_hdr *fontx_header = (fontx_hdr*)fontx->font;
  565
  566     vertex_t v_pos = *v0;
  567
  568     int length = strlen((const char *)str);
  569     short line_num[100];
  570     int line = 0;
  571
  572     float x_orig[100];
  573     x_orig[0] = 0;
  574
  575     float w = fontx_header->width;
  576     float h = fontx_header->height;
  577
  578     float wm = fontx->w_margin;
  579     float hm = fontx->h_margin;
  580
  581     // line_num is used to keep track of number of characters per line
  582     line_num[0] = 0;
  583
  584     switch (alignment)
  585     {
  586         default:
  587         case LEFT_ALIGN:
  588         {
  589             for (i = 0; i < length; i++)
  590             {
  591
  592                 while (str[i] == '\t' || str[i] == '\n')
  593                 {
  594
  595                     if(str[i] == '\n')
  596                     {
  597                         x_orig[line] = v_pos.x;
  598                         line++;
  599                         line_num[line] = 0;
  600                     }
  601
  602                     i++;
  603
  604                 }
  605
  606
  607                 if (i == length-1)
  608                 {
  609                     x_orig[line] = v_pos.x;
  610                     line++;
  611                 }
  612
  613             }
  614             break;
  615
  616         }
  617         case RIGHT_ALIGN:
  618         {
  619             for (i = 0; i < length; i++)
  620             {
  621
  622                 while (str[i] == '\t' || str[i] == '\n')
  623                 {
  624
  625                     if (str[i] == '\t')
  626                     {
  627                         line_num[line] += 4;
  628                     }
  629
  630                     if (str[i] == '\n')
  631                     {
  632                         x_orig[line] = v_pos.x - (line_num[line] * (w + wm));
  633                         line++;
  634                         line_num[line] = 0;
  635                     }
  636
  637                     i++;
  638
  639                 }
  640
  641
  642                 line_num[line]++;
  643
  644                 if (i == length-1)
  645                 {
  646                     x_orig[line] = v_pos.x - (line_num[line] * (w + wm));
  647                     line++;
  648                 }
  649
  650             }
  651             break;
  652
  653         }
  654         case CENTER_ALIGN:
  655         {
  656             for (i = 0; i < length; i++)
  657             {
  658
  659                 while (str[i] == '\t' || str[i] == '\n')
  660                 {
  661
  662                     if (str[i] == '\t')
  663                     {
  664                         line_num[line] += 4;
  665                     }
  666
  667                     if (str[i] == '\n')
  668                     {
  669                         x_orig[line] = v_pos.x - (line_num[line] * (w + wm))/2.0f;
  670                         line++;
  671                         line_num[line] = 0;
  672                     }
  673
  674                     i++;
  675
  676                 }
  677
  678                 line_num[line]++;
  679
  680                 if (i == length-1)
  681                 {
  682                     x_orig[line] = v_pos.x - (line_num[line] * (w + wm))/2.0f;
  683                     line++;
  684                 }
  685
  686             }
  687             break;
  688
  689         }
  690
  691     };
  692
  693     line = 0;
  694     v_pos.x = x_orig[0];
  695
  696     q = draw_prim_start(q,context,&charprim,c0);
  697
  698     for (j = 0; j < length; j++)
  699     {
  700
  701         while(str[j] == '\n' || str[j] == '\t')
  702         {
  703             if (str[j] == '\n')
  704             {
  705                 line++;
  706                 v_pos.y += h + hm;
  707                 v_pos.x = x_orig[line];
  708             }
  709             if (str[j] == '\t')
  710             {
  711                 v_pos.x += w * 5.0f;
  712             }
  713             j++;
  714         }
  715
  716         if (str[j] < 0x80)
  717         {
  718             q = draw_fontx_char(q,str[j],&v_pos,fontx);
  719         }
  720         else if (str[j] >= 0xA1 && str[j] <= 0xDF)
  721         {
  722             q = draw_fontx_char(q,str[j],&v_pos,fontx);
  723         }
  724
  725         v_pos.x += w + wm;
  726
  727     }
  728
  729     q = draw_prim_end(q,2,DRAW_XYZ_REGLIST);
  730
  731     return q;
  732
  733 }
  734
  735 qword_t *fontx_print_sjis(qword_t *q, int context, const unsigned char *str, int alignment, const vertex_t *v0, const color_t *c0, fontx_t *ascii, fontx_t *kanji)
  736 {
  737
  738     int i,j;
  739
  740     fontx_hdr *ascii_header = (fontx_hdr*)ascii->font;
  741     fontx_hdr *kanji_header = (fontx_hdr*)kanji->font;
  742
  743     vertex_t v_pos = *v0;
  744
  745     int length = strlen((const char *)str);
  746
  747     int line = 0;
  748     short halfwidth[100];
  749     short fullwidth[100];
  750     float x_orig[100];
  751     x_orig[0] = 0;
  752
  753     unsigned short wide;
  754
  755     float hw = ascii_header->width;
  756
  757     float fw = kanji_header->width;
  758     float h = kanji_header->height;
  759
  760     float wm = kanji->w_margin;
  761     float hm = kanji->h_margin;
  762
  763     // line_num is used to keep track of number of characters per line
  764     halfwidth[0] = 0;
  765     fullwidth[0] = 0;
  766
  767     switch (alignment)
  768     {
  769         default:
  770         case LEFT_ALIGN:
  771         {
  772             for (i = 0; i < length; i++)
  773             {
  774
  775                 while (str[i] == '\t'|| str[i] == '\n')
  776                 {
  777                     if (str[i] == '\t')
  778                     {
  779                         halfwidth[line] += 4;
  780                     }
  781                     if (str[i] == '\n')
  782                     {
  783                         x_orig[line] = v_pos.x;
  784                         line++;
  785                         halfwidth[line] = 0;
  786                         fullwidth[line] = 0;
  787                     }
  788                     i++;
  789                 }
  790
  791
  792                 if (i == length-1)
  793                 {
  794                     x_orig[line] = v_pos.x;
  795                     line++;
  796                 }
  797
  798             }
  799             break;
  800
  801         }
  802         case RIGHT_ALIGN:
  803         {
  804             for (i = 0; i < length; i++)
  805             {
  806
  807                 while (str[i] == '\t'|| str[i] == '\n')
  808                 {
  809                     if (str[i] == '\t')
  810                     {
  811                         halfwidth[line] += 4;
  812                     }
  813                     if (str[i] == '\n')
  814                     {
  815                         x_orig[line] = v_pos.x - ((halfwidth[line] * (hw+wm)) + (fullwidth[line] * (fw + wm)));;
  816                         line++;
  817                         halfwidth[line] = 0;
  818                         fullwidth[line] = 0;
  819                     }
  820                     i++;
  821                 }
  822
  823                 if (str[i] < 0x80)
  824                 {
  825                     halfwidth[line]++;
  826                 }
  827                 else if (str[i] >= 0xA1 && str[i] <= 0xDF)
  828                 {
  829                     halfwidth[line]++;
  830                 }
  831                 else if (str[i] >= 0x81 && str[i] <= 0x9F)
  832                 {
  833                     fullwidth[line]++;
  834                 }
  835                 else if (str[i] >= 0xE0 && str[i] <= 0xEF)
  836                 {
  837                     fullwidth[line]++;
  838                 }
  839
  840                 if (i == length-1)
  841                 {
  842                     x_orig[line] = v_pos.x - ((halfwidth[line] * (hw+wm)) + (fullwidth[line] * (fw + wm)));
  843                     line++;
  844                 }
  845
  846             }
  847             break;
  848
  849         }
  850         case CENTER_ALIGN:
  851         {
  852             for (i = 0; i < length; i++)
  853             {
  854
  855                 while (str[i] == '\t'|| str[i] == '\n')
  856                 {
  857                     if (str[i] == '\t')
  858                     {
  859                         halfwidth[line] += 4;
  860                     }
  861                     if (str[i] == '\n')
  862                     {
  863                         x_orig[line] = v_pos.x - ((halfwidth[line] * (hw+wm)) + (fullwidth[line] * (fw + wm)))/2.0f;
  864                         line++;
  865                         halfwidth[line] = 0;
  866                         fullwidth[line] = 0;
  867                     }
  868                     i++;
  869                 }
  870
  871                 if (str[i] < 0x80)
  872                 {
  873                     halfwidth[line]++;
  874                 }
  875                 else if (str[i] >= 0xA1 && str[i] <= 0xDF)
  876                 {
  877                     halfwidth[line]++;
  878                 }
  879                 else if (str[i] >= 0x81 && str[i] <= 0x9F)
  880                 {
  881                     fullwidth[line]++;
  882                 }
  883                 else if (str[i] >= 0xE0 && str[i] <= 0xEF)
  884                 {
  885                     fullwidth[line]++;
  886                 }
  887
  888                 if (i == length-1)
  889                 {
  890                     x_orig[line] = v_pos.x - ((halfwidth[line] * (hw+wm)) + (fullwidth[line] * (fw + wm)))/2.0f;
  891                     line++;
  892                 }
  893
  894             }
  895             break;
  896
  897         }
  898
  899     };
  900
  901     line = 0;
  902     v_pos.x = x_orig[0];
  903
  904     q = draw_prim_start(q,context,&charprim,c0);
  905
  906     for (j = 0; j < length; j++)
  907     {
  908
  909
  910         while(str[j] == '\n' || str[j] == '\t')
  911         {
  912             if (str[j] == '\n')
  913             {
  914                 line++;
  915                 v_pos.y += h + hm;
  916                 v_pos.x = x_orig[line];
  917             }
  918             if (str[j] == '\t')
  919             {
  920                 v_pos.x += hw * 5.0f;
  921             }
  922             j++;
  923         }
  924
  925         if (str[j] < 0x80)
  926         {
  927             q = draw_fontx_char(q,str[j],&v_pos,ascii);
  928             v_pos.x += hw + wm;
  929         }
  930         else if (str[j] >= 0xA1 && str[j] <= 0xDF)
  931         {
  932             q = draw_fontx_char(q,str[j],&v_pos,ascii);
  933             v_pos.x += hw + wm;
  934         }
  935         else if (str[j] >= 0x81 && str[j] <= 0x9F)
  936         {
  937             wide = str[j++]<<8;
  938             wide += str[j];
  939             q = draw_fontx_char(q,wide,&v_pos,kanji);
  940             v_pos.x += fw + wm;
  941         }
  942         else if (str[j] >= 0xE0 && str[j] <= 0xEF)
  943         {
  944             wide = str[j++]<<8;
  945             wide += str[j];
  946             q = draw_fontx_char(q,wide,&v_pos,kanji);
  947             v_pos.x += fw + wm;
  948         }
  949         else
  950         {
  951             v_pos.x += fw + wm;
  952         }
  953
  954     }
  955
  956     q = draw_prim_end(q,2,DRAW_XYZ_REGLIST);
  957
  958     return q;
  959
  960 }