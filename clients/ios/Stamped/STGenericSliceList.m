//
//  STGenericSliceList.m
//  Stamped
//
//  Created by Landon Judkins on 4/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericSliceList.h"

@interface STGenericSliceList ()

@end

@implementation STGenericSliceList

@synthesize genericSlice = genericSlice_;

- (id)init
{
  self = [super init];
  if (self) {
  }
  return self;
}

- (void)dealloc
{
  [genericSlice_ release];
  [super dealloc];
}

- (void)setGenericSlice:(STGenericSlice *)genericSlice {
  [genericSlice_ autorelease];
  genericSlice_ = [genericSlice retain];
  [self reload];
}

- (STCancellation*)fetchWithRange:(NSRange)range
                      andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  //TODO consider adding baseOffset and baseLimit functionallity
  STGenericSlice* slice = [self.genericSlice resizedSliceWithLimit:[NSNumber numberWithInteger:range.length] andOffset:[NSNumber numberWithInteger:range.location]];
  return [self makeStampedAPICallWithSlice:slice andCallback:block];
}

- (STCancellation*)makeStampedAPICallWithSlice:(STGenericSlice*)slice 
                                   andCallback:(void (^)(NSArray* results, NSError* error, STCancellation* cancellation))block {
  NSAssert1(NO, @"Should be implemented in subclass %@", self);
  return nil;
}

@end
