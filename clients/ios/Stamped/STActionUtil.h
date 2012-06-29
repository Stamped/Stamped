//
//  STActionUtil.h
//  Stamped
//
//  Created by Landon Judkins on 6/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STActionDelegate.h"

@interface STActionUtil : NSObject <STActionDelegate>

+ (STActionUtil*)sharedInstance;

+ (NSString*)previewURLForItem:(id<STPlaylistItem>)item;

+ (NSString*)sourceIDForItem:(id<STPlaylistItem>)item withSource:(NSString*)source;

+ (BOOL)playable:(id<STPlaylistItem>)item;

@end
