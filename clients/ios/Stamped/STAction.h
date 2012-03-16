//
//  STActions.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STSource.h"

@protocol STAction <NSObject>

@property (nonatomic, readonly, retain) NSString* action;
@property (nonatomic, readonly, retain) NSString* name;
@property (nonatomic, readonly, retain) NSArray<STSource>* sources;

@end
