//
//  STHours.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STHours <NSObject>

@property (nonatomic, readonly, retain) NSString* open;
@property (nonatomic, readonly, retain) NSString* close;
@property (nonatomic, readonly, retain) NSString* desc;

@end
