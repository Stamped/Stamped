//
//  STSimpleSource.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleSource.h"

@implementation STSimpleSource

@synthesize name = name_;
@synthesize source = source_;
@synthesize sourceData = sourceData_;
@synthesize sourceID = sourceID_;
@synthesize link = link_;
@synthesize icon = icon_;
@synthesize endpoint = endpoint_;
@synthesize endpointData = endpointData_;
@synthesize completionEndpoint = completionEndpoint_;
@synthesize completionData = completionData_;

- (id)initWithCoder:(NSCoder *)decoder {
  self = [super init];
  if (self) {
    name_ = [[decoder decodeObjectForKey:@"name"] retain];
    source_ = [[decoder decodeObjectForKey:@"source"] retain];
    sourceData_ = [[decoder decodeObjectForKey:@"sourceData"] retain];
    sourceID_ = [[decoder decodeObjectForKey:@"sourceID"] retain];
    link_ = [[decoder decodeObjectForKey:@"link"] retain];
    icon_ = [[decoder decodeObjectForKey:@"icon"] retain];
    endpoint_ = [[decoder decodeObjectForKey:@"endpoint"] retain];
    endpointData_ = [[decoder decodeObjectForKey:@"endpointData"] retain];
    completionEndpoint_ = [[decoder decodeObjectForKey:@"completionEndpoint"] retain];
    completionData_ = [[decoder decodeObjectForKey:@"completionData"] retain];
  }
  return self;
}

- (void)dealloc {
  self.name = nil;
  self.source = nil;
  self.sourceID = nil;
  self.link = nil;
  self.icon = nil;
  [sourceData_ release];
  [endpoint_ release];
  [endpointData_ release];
  [completionEndpoint_ release];
  [completionData_ release];
  [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
  [encoder encodeObject:self.name forKey:@"name"];
  [encoder encodeObject:self.source forKey:@"source"];
  [encoder encodeObject:self.sourceID forKey:@"sourceID"];
  [encoder encodeObject:self.link forKey:@"link"];
  [encoder encodeObject:self.icon forKey:@"icon"];
  [encoder encodeObject:self.sourceData forKey:@"sourceData"];
  [encoder encodeObject:self.endpoint forKey:@"endpoint"];
  [encoder encodeObject:self.completionEndpoint forKey:@"completionEndpoint"];
  [encoder encodeObject:self.completionData forKey:@"completionData"];
}

+ (RKObjectMapping*)mapping {
  RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleSource class]];
  
  [mapping mapAttributes:
   @"name",
   @"source",
   @"link",
   @"icon",
   @"endpoint",
   nil];
  
  [mapping mapKeyPathsToAttributes:
   @"source_id",@"sourceID",
   @"source_data", @"sourceData",
   @"endpoint_data", @"endpointData",
   @"completion_endpoint", @"completionEndpoint",
   @"completion_data", @"completionData",
   nil];
  
  return mapping;
}

+ (STSimpleSource*)sourceWithSource:(NSString*)source andSourceID:(NSString*)sourceID {
  STSimpleSource* sourceObj = [[[STSimpleSource alloc] init] autorelease];
  sourceObj.source = source;
  sourceObj.sourceID = sourceID;
  return sourceObj;
}

@end
