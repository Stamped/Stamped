//
//  STPlaylistItem.h
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STSource;

@protocol STPlaylistItem <NSObject>

@property (nonatomic, readonly, retain) NSString* name;
@property (nonatomic, readonly, assign) NSInteger num;
@property (nonatomic, readonly, assign) NSInteger length;
@property (nonatomic, readonly, retain) NSString* icon;
@property (nonatomic, readonly, retain) NSString* link;
@property (nonatomic, readonly, retain) NSArray<STSource>* sources;

@end
