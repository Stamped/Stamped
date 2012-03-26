//
//  STEntityDetailView.m
//  Stamped
//
//  Created by Landon Judkins on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STEntityDetailView.h"

@interface STEntityDetailView()

@property (nonatomic, readonly) NSMutableDictionary* operations;
@property (nonatomic, readonly) NSMutableDictionary* components;

@end

@implementation STEntityDetailView

- (id)initWithDelegate:(id<STViewDelegate>)delegate andEntityDetail:(id<STEntityDetail>)anEntityDetail;
{
    self = [super initWithDelegate:delegate andFrame:CGRectMake(0, 0, 320, 0)];
    if (self) {
      
    }
    return self;
}

@end
