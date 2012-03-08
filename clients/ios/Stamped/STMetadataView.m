//
//  STMetadataView.m
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STMetadataView.h"

@interface STMetadataView ()

- (void)commonInit:(id<STMetadata>)metadata;

@end

@implementation STMetadataView

- (id)initWithMetadata:(id<STMetadata>)metadata {
  self = [self initWithFrame:CGRectZero];
  if (self) {
    [self commonInit:metadata];
  }
  return self;
}

- (void)commonInit:(id<STMetadata>)metadata {
  
}

@end
