//
//  STSimplePreviews.m
//  Stamped
//
//  Created by Landon Judkins on 4/24/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimplePreviews.h"
#import "STSimpleUser.h"
#import "STSimpleComment.h"
#import "STSimpleStampPreview.h"

@implementation STSimplePreviews

@synthesize comments = comments_;
@synthesize likes = likes_;
@synthesize todos = todos_;
@synthesize credits = credits_;
@synthesize stamps = stamps_;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        comments_ = [[decoder decodeObjectForKey:@"comments"] retain];
        likes_ = [[decoder decodeObjectForKey:@"likes"] retain];
        todos_ = [[decoder decodeObjectForKey:@"todos"] retain];
        credits_ = [[decoder decodeObjectForKey:@"credits"] retain];
        stamps_ = [[decoder decodeObjectForKey:@"stamps"] retain];
    }
    return self;
}

- (void)dealloc
{
    [comments_ release];
    [likes_ release];
    [todos_ release];
    [credits_ release];
    [stamps_ release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.comments forKey:@"comments"];
    [encoder encodeObject:self.likes forKey:@"likes"];
    [encoder encodeObject:self.todos forKey:@"todos"];
    [encoder encodeObject:self.credits forKey:@"credits"];
    [encoder encodeObject:self.stamps forKey:@"stamps"];
}

+ (RKObjectMapping*)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimplePreviews class]];
    
    [mapping mapRelationship:@"comments" withMapping:[STSimpleComment mapping]];
    [mapping mapRelationship:@"likes" withMapping:[STSimpleUser mapping]];
    [mapping mapRelationship:@"todos" withMapping:[STSimpleUser mapping]];
    [mapping mapRelationship:@"credits" withMapping:[STSimpleStampPreview mapping]];
    [mapping mapRelationship:@"stamp" withMapping:[STSimpleStampPreview mapping]];
    
    return mapping;
}

+ (STSimplePreviews*)previewsWithPreviews:(id<STPreviews>)previews {
    STSimplePreviews* copy = [[[STSimplePreviews alloc] init] autorelease];
    copy.comments = previews.comments;
    copy.likes = previews.likes;
    copy.todos = previews.todos;
    copy.credits = previews.credits;
    copy.stamps = previews.stamps;
    return copy;
}

@end
