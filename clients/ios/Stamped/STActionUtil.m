//
//  STActionUtil.m
//  Stamped
//
//  Created by Landon Judkins on 6/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActionUtil.h"
#import "STSimplePlaylistItem.h"
#import "STSimpleAction.h"
#import "STPlayerPopUp.h"
#import "STConfiguration.h"
#import "STPlayer.h"
#import "STRdio.h"

@implementation STActionUtil

static id _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STActionUtil alloc] init];
}

+ (STActionUtil *)sharedInstance {
    return _sharedInstance;
}

- (BOOL)canHandleSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext *)context {
    return [self didChooseSource:source forAction:action withContext:context shouldExecute:NO];
}

- (void)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext *)context {
    [self didChooseSource:source forAction:action withContext:context shouldExecute:YES];
}

- (BOOL)didChooseSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context shouldExecute:(BOOL)flag {
    BOOL handled = NO;
    if ([action isEqualToString:@"listen"]) {
        NSArray<STPlaylistItem>* items = [self itemsForSource:source forAction:action withContext:context];
        if (items.count) {
            handled = TRUE;
            if (flag) {
                NSInteger startIndex = 0;
                if (context.playlistItem) {
                    id<STPlaylistItem> primary = context.playlistItem;
                    for (NSInteger i = 0; i < items.count; i++) {
                        id<STPlaylistItem> item = [items objectAtIndex:i];
                        if ([[item name] isEqualToString:[primary name]]) {
                            NSString* rdioID = [STActionUtil sourceIDForItem:primary withSource:@"rdio"];
                            NSString* otherRdioID = [STActionUtil sourceIDForItem:item withSource:@"rdio"];
                            if (rdioID == otherRdioID || [rdioID isEqualToString:otherRdioID]) {
                                NSString* preview = [STActionUtil previewURLForItem:primary];
                                NSString* otherPreview = [STActionUtil previewURLForItem:item];
                                if (preview == otherPreview || [preview isEqualToString:otherPreview]) {
                                    startIndex = i;
                                    break;
                                }
                            }
                        }
                    }
                }
                if ([[STRdio sharedRdio] connected]) {
                    [[STRdio sharedRdio] ensureLoginWithCompletionBlock:^{
                        [STPlayerPopUp presentWithItems:items clear:![STConfiguration flag:STPlayerCummulativeKey] startIndex:startIndex];
                    }];
                }
                else {
                    [STPlayerPopUp presentWithItems:items clear:![STConfiguration flag:STPlayerCummulativeKey] startIndex:startIndex];
                }
            }
        }
    }
    return handled;
}

+ (NSString*)sourceIDForItem:(id<STPlaylistItem>)item withSource:(NSString*)source {
    if (item.action.sources.count) {
        for (id<STSource> source2 in item.action.sources) {
            if ([source2.source isEqualToString:source]) {
                return source2.sourceID;
            }
        }
    }
    return nil;
}

+ (NSString*)previewURLForItem:(id<STPlaylistItem>)item {
    if (item.action.sources.count) {
        for (id<STSource> source in item.action.sources) {
            if ([source sourceData]) {
                NSString* previewURL = [[source sourceData] objectForKey:@"preview_url"];
                if (previewURL) {
                    return previewURL;
                }
            }
        }
    }
    return nil;
}

- (NSArray<STPlaylistItem>*)itemsForSource:(id<STSource>)source forAction:(NSString*)action withContext:(STActionContext*)context {
    NSArray<STImage>* images = nil;
    if (context.entityDetail.images.count) {
        id<STImageList> first = [context.entityDetail.images objectAtIndex:0];
        images = first.sizes;
    }
    NSString* defaultSubtitle = nil;
    NSString* subcategory = context.entityDetail.subcategory;
    if ([subcategory isEqualToString:@"artist"]) {
        defaultSubtitle = [NSString stringWithFormat:@"By %@", context.entityDetail.title];
    }
    else if ([subcategory isEqualToString:@"album"]) {
        defaultSubtitle = [NSString stringWithFormat:@"From %@", context.entityDetail.title];
    }
    else if ([subcategory isEqualToString:@"song"]) {
        defaultSubtitle = context.entityDetail.caption;
    }
    BOOL connectedToRdio = [[STRdio sharedRdio] connected];
    NSArray<STPlaylistItem>* potentialMatches = context.entityDetail.playlist.data;
    if (potentialMatches.count == 0 && [context.entityDetail.subcategory isEqualToString:@"song"]) {
        id<STAction> listenAction = nil;
        if (context.entityDetail.actions.count) {
            for (id<STActionItem> actionItem in context.entityDetail.actions) {
                id<STAction> curAction = [actionItem action];
                if ([[curAction type] isEqualToString:@"listen"]) {
                    listenAction = curAction;
                    break;
                }
            }
        }
        STSimplePlaylistItem* item = [[[STSimplePlaylistItem alloc] init] autorelease];
        item.name = context.entityDetail.title;
        if (!listenAction) {
            listenAction = [STSimpleAction actionWithType:action andSource:source];
        }
        item.action = listenAction;
        if (!item.images) {
            item.images = images;
        }
        if (!item.subtitle) {
            item.subtitle = defaultSubtitle;
        }
        //TODO memory leak; resolve
        [item retain];
        potentialMatches = [NSArray arrayWithObject:item];
    }
    NSMutableArray<STPlaylistItem>* array = [NSMutableArray array];
    for (id<STPlaylistItem> item in potentialMatches) {
        NSString* itemID = [STActionUtil sourceIDForItem:item withSource:@"rdio"];
        NSString* previewURL = [STActionUtil previewURLForItem:item];
        if ((itemID && connectedToRdio) || previewURL) {
            STSimplePlaylistItem* simpleItem = [[STSimplePlaylistItem playlistItemWithItem:item] retain];
            [array addObject:simpleItem];
            if (!simpleItem.images) {
                simpleItem.images = images;
            }
            if (!simpleItem.subtitle) {
                simpleItem.subtitle = defaultSubtitle;
            }
        }
    }
    return array;
}

+ (BOOL)playable:(id<STPlaylistItem>)item {
    if ([[STRdio sharedRdio] connected] && [self sourceIDForItem:item withSource:@"rdio"]) {
        return YES;
    }
    if ([self previewURLForItem:item]) {
        return YES;
    }
    return NO;
}

@end
