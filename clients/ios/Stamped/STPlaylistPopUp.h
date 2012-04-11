//
//  STPlaylistPopUp.h
//  Stamped
//
//  Created by Landon Judkins on 4/10/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STTablePopUp.h"

@interface STPlaylistPopUp : STTablePopUp

- (id)initWithSource:(id<STSource>)source action:(NSString*)action andContext:(STActionContext*)context;

- (NSString*)getItemId:(id<STPlaylistItem>)item;

@property (nonatomic, readonly, retain) NSArray<STPlaylistItem>* playlistItems;

@end
