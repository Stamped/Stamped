//
//  STCommentSlice.m
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCommentSlice.h"

@implementation STCommentSlice

@synthesize stampID = _stampID;

- (void)dealloc
{
  [_stampID release];
  [super dealloc];
}

- (NSMutableDictionary*)asDictionaryParams {
  NSMutableDictionary* dict = [super asDictionaryParams];
  if (self.stampID) {
    [dict setObject:self.stampID forKey:@"stamp_id"];
  }
  return dict;
}

+ (STCommentSlice*)sliceForStampID:(NSString*)stampID offset:(NSInteger)offset limit:(NSInteger)limit {
  //TODO
  return nil;
}

- (id)resizedSliceWithLimit:(NSNumber*)limit andOffset:(NSNumber*)offset {
  STCommentSlice* copy = [super resizedSliceWithLimit:limit andOffset:offset];
  copy.stampID = self.stampID;
  return copy;
}

@end
